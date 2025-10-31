#!/usr/bin/env python3

import logging
from lxml import etree
from pathlib import Path


logger = logging.getLogger(__name__)

class ManifestElementInterface:
    """Interface class for using manifest elements as objects with
    their variables as actual attributes.
    e.g
        the below element from the manifest could be passed this class
        <remote name="example" fetch="https://example.com"/>

        The object generated from this class would have the following attributes
        object.name == "example.git"
        object.fetch == "https://example.com"

    Attributes:
        self._element (_Element): The original xml element passed into this interface.
        self._manifest (ScManifest): The ScManifest object this element belongs to.
    """
    def __init__(self, element: etree._Element, manifest: "ScManifest"):
        # Use super() due to overriding __setattr__
        super().__setattr__('_element', element)
        super().__setattr__('_manifest', manifest)

    def __getattr__(self, name: str) -> str | None:
        value = self._element.attrib.get(name)
        if value is None:
            return self._manifest.get_default_value(name)
        return value
    
    def __setattr__(self, name: str, value: str):
        """Setting attr on the interface sets the attribute on the element."""
        self._element.attrib[name] = value
    
    def __delattr__(self, name: str):
        """Deleting attr on the interface deletes the attribute on the element."""
        try:
            del self._element.attrib[name]
        except KeyError:
            raise AttributeError(
                f"Attribute '{name}' not set on element (may be inherited from <default>)"
            )

    def remove(self):
        parent = self._element.getparent()
        parent.remove(self._element)

    @property
    def children(self) -> list["ManifestElementInterface"]:
        return [ManifestElementInterface(child, self._manifest) for child in self._element]
    
    def add_child(self, name: str, attributes: dict[str, str]) -> "ManifestElementInterface":
        child = etree.SubElement(self._element, name, attrib=attributes)
        return ManifestElementInterface(child, self._manifest)
    
    def search_children(self, name: str) -> list["ManifestElementInterface"] | None:
        """Search the children of the current node for a child with the given name

        Args:
            name (str): The name of the element tag you're looking for.

        Returns:
            list[ManifestElementInterface] | None: A list of all the children that match
                the name. None if no children with the given name are found.
        """
        return [child for child in self.children if child._element.tag == name]

class ProjectElementInterface(ManifestElementInterface):
    """Extends the ManifestElementInterface to add functionality for getting attributes from
    annotation elements. Specifically designed to handle <project.../> elements from the manifest.
    """
    @property
    def path(self) -> str:
        return self._element.attrib.get('path') or self._element.attrib.get('name')
    
    @property
    def lock_status(self) -> str | None:
        """Get the value of the annotation element with name set to GIT_LOCK_STATUS.
        
        Returns:
            str: The value of the annotation element with name set to GIT_LOCK_STATUS.
        """
        annotations = self.search_children('annotation')
        
        if annotations:
            matched_annotations = [a for a in annotations if a.name == 'GIT_LOCK_STATUS']
            if matched_annotations:
                return matched_annotations[0].value
        
        return None
    
    @property
    def alternative_master(self) -> str | None:
        return self._get_alternative_branch('master')

    @property
    def alternative_develop(self) -> str | None:
        return self._get_alternative_branch('develop')
    
    def _get_alternative_branch(self, branch: str) -> str | None:
        """Get the value of the first annotation element with
        name set to GIT_FLOW_BRANCH_<argument branch> or GIT_FLOW_SUFFIX
        
        Args:
          branch (str): The branch we are looking for an alternative for.
        
        Returns:
            str: The value of the annotation element with name set to 
                GIT_FLOW_BRANCH_<argument branch> or GIT_FLOW_SUFFIX.
        """
        annotations = self.search_children('annotation')
        if not annotations:
            return None
        
        branch_annotation = f"GIT_FLOW_BRANCH_{branch.upper()}"
        suffix_annotation = "GIT_FLOW_SUFFIX"

        for annotation in annotations:
            if annotation.name == branch_annotation:
                return annotation.value
            if annotation.name == suffix_annotation:
                return f"{branch}-{annotation.value}"
        
        return None

class ScManifest:
    """Represents an sc manifest."""
    def __init__(self, manifest_path: str | Path):
        self.manifests: dict[Path, etree._ElementTree] = {}
        self.manifest_path = Path(manifest_path)
        if not self.manifest_path.exists():
            raise FileNotFoundError(
                'Cannot find manifest path supplied: {manifest_path}'.format(
                    manifest_path=self.manifest_path))

        self.xml_parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(self.manifest_path, self.xml_parser)
        self.manifests[self.manifest_path] = tree

        root = tree.getroot()
        for inc in root.findall('include'):
            self._parse_include(inc.get('name'), self.manifest_path.parent)

        defaults = self._find_all('default') 
        if len(defaults) > 1:
            raise ValueError("More than one <default> element.")
        elif len(defaults) == 1:
            self._default = defaults[0]
        else:
            self._default = None

    @classmethod
    def from_repo_root(cls, repo_root: Path | str) -> "ScManifest":
        """Parse a repo's projects manifest by it's root.

        Args:
            repo_root (Path | str): Path to .repo file of a repo project.

        Raises:
            Exception: If the manifest.xml in .repo is not as expected. Top level manifest.xml
                should have a single include which points to the projects manifest.

        Returns:
            ScManifest: The manifest supplying the repo project.
        """    
        manifest_xml = Path(repo_root) / 'manifest.xml'
        if manifest_xml.is_symlink():
            return cls(repo_root / manifest_xml.readlink())
        else:
            root = etree.parse(manifest_xml).getroot()
            included = root.findall('include')
            if len(included) != 1:
                raise ValueError(
                    "Incorrect number of included manifests in " + str(manifest_xml) +
                    "! Should be one but is " + len(included)
                )
            return cls(manifest_xml.parent / 'manifests' / included[0].attrib['name'])

    @property
    def remotes(self) -> list[ManifestElementInterface]:
        return [ManifestElementInterface(rem, self) for rem in self._find_all('remote')]

    @property
    def projects(self) -> list[ProjectElementInterface]:
        """Get all project attributes, removing any specified by remove-project attributes
        """        
        projects = [ProjectElementInterface(proj, self) for 
                    proj in self._find_all('project')]
        
        projects = self._apply_remove_project_attributes(projects)
        
        return projects
    
    @property
    def remove_projects(self) -> list[ManifestElementInterface]:
        return [ManifestElementInterface(proj, self) for 
                proj in self._find_all('remove-project')]

    @property
    def post_sync_scripts(self) -> list[ManifestElementInterface]:
        return [ManifestElementInterface(ps, self) for ps in self._find_all('post-sync')]

    @property
    def default(self) -> ManifestElementInterface | None:
        return ManifestElementInterface(self._default, self)

    @property
    def git_flow(self) -> ManifestElementInterface | None:
        git_flow = self._find_all('git_flow')
        return ManifestElementInterface(git_flow[0], self) if len(git_flow) != 0 else None
    
    @property
    def submanifests(self) -> list["ScManifest"]:
        subman_elems = self._find_all('submanifest')
        return [ScManifest(self.manifest_path / sub.get('path')) for sub in subman_elems]
    
    def get_default_value(self, name: str) -> str | None:
        return self._default.get(name) if self._default is not None else None

    def get_project_by_name(self, project_name: str) -> ProjectElementInterface:
        """Get a ProjectElementInterface object for the project with the given name.
        
        Args:
            project_name (str): The name of the project you want to get.

        Raises:
            AttributeError: When no project with the given name can be found.

        Returns:
            ProjectElementInterface: ProjectElementInterface object with name 
                attribute matching project_name.
        """
        for project in self.projects:
            if project.name == project_name:
                return project
        raise AttributeError ('No project found with name: {}'.format(project_name))

    def get_project_by_path(self, project_path: str | Path) -> ProjectElementInterface:
        """Get a ProjectElementInterface object for the project with the given path.
        
        Args:
            project_path (str | Path): The path to the project you want to get.

        Raises:
            AttributeError: When no project with the given path can be found.

        Returns:
            ProjectElementInterface: ProjectElementInterface object with path 
                attribute matching project_path.
        """
        for project in self.projects:
            if project.path == str(project_path):
                return project
        raise AttributeError('No project found with path: {}'.format(project_path))

    def get_remote_by_name(self, remote_name: str) -> ManifestElementInterface:
        """Get a `ManifestElementInterface` object for the remote with the given name.
        
        Args:
            remote_name (str): The name of the remote to get.

        Raises:
            AttributeError: When no remote with the given name can be found.

        Returns:
            ManifestElementInterface: The remote object with the name
                that matches the remote_name argument.
        """
        for remote in self.remotes:
            if remote.name == remote_name:
                return remote
        raise AttributeError ('No project found with name: {}'.format(remote_name))
    
    def write(self):
        for source_file, tree in self.manifests.items():
            with open(source_file, 'wb') as file:
                tree.write(file, pretty_print=True, xml_declaration=True)

    def _find_all(self, element_name: str) -> list[etree._Element]:
        """Find all top level elements by name in all included manifests."""
        results = []
        for tree in self.manifests.values():
            elements = tree.getroot().findall(element_name)
            results.extend(elements)
        return results
                
    def _parse_include(self, path: Path | str, include_root: Path | str):
        full_path = Path(include_root) / path
        include_manifest: etree._ElementTree = etree.parse(str(full_path), self.xml_parser)
        self.manifests[full_path] = include_manifest

        for subelement in include_manifest.getroot():
            if subelement.tag == "include":
                if subelement.get('name') == None:
                    raise ValueError(
                        f"Include element in manifest {full_path} missing name!")

                self._parse_include(subelement.get('name'), full_path.parent)

    def _apply_remove_project_attributes(
            self, projects: list[ProjectElementInterface]) -> list[ProjectElementInterface]:
        """Remove projects specified by <remove-project> attributes.

        If <remove-project> has both name and path values it must match both otherwise
        just match the name or path value.
        """
        for rm in self.remove_projects:
            for project in projects:
                if rm.name == project.name and rm.path == project.path:
                    projects.remove(project)
                    break
                elif rm.name == project.name and rm.path == None:
                    projects.remove(project)
                    break
                elif rm.name == None and rm.path == project.path:
                    projects.remove(project)
                    break
                
        return projects
