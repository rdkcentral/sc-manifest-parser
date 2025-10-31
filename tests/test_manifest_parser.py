#/usr/bin/env python3

from pathlib import Path
import unittest

from sc_manifest_parser.sc_manifest_parser import ScManifest, ManifestElementInterface

class ManifestParserTester(unittest.TestCase):

    _expected_manifest_values = {
        'remotes': [
            {
                'name' : 'external',
                'fetch' : 'ssh://git@team.com'
            }
            ],
        'projects':[
            {
                'groups': 'Group1',
                'name': 'test_repo/repo_flow_test_projecta.git',
                'path': 'dira',
                'revision': '823a24794c1d980aaaa08fbd0a8dd95d1a1a8c39',
                'alternative_develop': 'develop-v2',
                'alternative_master': 'master-v2',
            },
            {
                'groups': 'Group2',
                'name': 'test_repo/repo_flow_test_projectb.git',
                'path': 'dirb',
                'revision': 'd017db0c2d8886a2f6512de5b8a5eac9ebc735d4',
                'alternative_develop': 'develop_2',
            },
            {
                'groups': 'Group3',
                'name': 'test_repo/repo_flow_test_projectc.git',
                'path': 'dirc',
                'revision': '7b4a84290431aa334abb275c432b41c2a72d63f6',
                'alternative_master': 'master_2',
            },
            {
                'groups': 'Group4',
                'name': 'test_repo/repo_flow_test_projectd.git',
                'path': 'dird',
                'revision': 'd82d29be14fce3ad91cddea1a559d4ac996bb64b',
                'lock_status': 'READ_ONLY',
                'linkfiles': 1
            }
        ],
        'post_sync_scripts':[
            {
                'path':'post-sync.sh'
            }
        ]
    }
    def setUp(self) -> None:
        self._manifest = ScManifest(Path(__file__).resolve().parent/'resources'/'test_manifest.xml')

    def test_remote_parsing(self):
        remotes = self._manifest.remotes
        expected_remotes = ManifestParserTester._expected_manifest_values.get('remotes')
        self.assertEqual(len(remotes),len(expected_remotes),'Expected {expected} remote to be found in {manifest}. [{remotes}] remotes found.'.format(expected=len(expected_remotes),manifest=self._manifest, remotes=len(remotes)))
        self._test_get_remote_by_name()
        self._test_get_remote_by_name_negative()
        for index,remote in enumerate(remotes):
            expected_name = expected_remotes[index].get('name')
            expected_fetch = expected_remotes[index].get('fetch')
            self.assertEqual(remote.name,expected_name,'Expected remotes name variable to be {expected_remote_name}. Remotes name was [{remote_name}]'.format(expected_remote_name=expected_name,remote_name=remote.name))
            self.assertEqual(remote.fetch,expected_fetch,'Expected remotes fetch variable to be {expected_fetch}. Remotes fetch was[{remote_fetch}]'.format(expected_fetch=expected_fetch,remote_fetch=remote.fetch))
            self.assertIsNone(remote.example,'Remote example variable was [{}], expected None'.format(remote.example))

    def _test_get_remote_by_name(self):
        try:
            self._manifest.get_remote_by_name('external')
        except AttributeError as e:
            self.fail(' '.join(e.args))

    def _test_get_remote_by_name_negative(self):
        error = False
        try:
            self._manifest.get_remote_by_name('error')
        except AttributeError:
            error= True
        self.assertTrue(error,'Expected AttributeError after get_remote_by_name with non-existant name')

    def test_projects(self):
        projects = self._manifest.projects
        expected_projects = self._expected_manifest_values.get('projects')
        self.assertEqual(len(projects),len(expected_projects),'Expected to find {expected} projects in {manifest}. [{projects}] projects found.'.format(expected=len(expected_projects),manifest=self._manifest,projects=len(projects)))
        try:
            project_a = self._manifest.get_project_by_name('test_repo/repo_flow_test_projecta.git')
            self._test_each_project([project_a],expected_projects)
        except AttributeError as e:
            self.fail(' '.join(e.args))
        try:
            project_a = self._manifest.get_project_by_path('dira')
            self._test_each_project([project_a],expected_projects)
        except AttributeError as e:
            self.fail(' '.join(e.args))
        error = False
        try:
            self._manifest.get_project_by_name('error')
        except AttributeError:
            error = True
        self.assertTrue(error,'Expected AttributeError when using get_project_by_name with non-existant name')
        error = False
        try:
            self._manifest.get_project_by_path('error')
        except AttributeError:
            error = True
        self.assertTrue(error, 'Expected AttributeError when using get_project_by_path with non-existant path')
        self._test_each_project(projects, expected_projects)

    def _test_each_project(self,projects, expected_projects):
        for index, project in enumerate(projects):
            expected_groups = expected_projects[index].get('groups')
            self._test_project_groups(project,expected_groups)
            expected_name = expected_projects[index].get('name')
            self._test_project_names(project,expected_name)
            expected_path = expected_projects[index].get('path')
            self._test_project_path(project,expected_path)
            expected_revision = expected_projects[index].get('revision')
            self._test_project_revision(project,expected_revision)
            expected_develop = expected_projects[index].get('alternative_develop')
            self._test_project_alternative_develop(project,expected_develop)
            expected_master = expected_projects[index].get('alternative_master')
            self._test_project_alternative_master(project,expected_master)
            expected_lock_status = expected_projects[index].get('lock_status')
            self._test_project_lock_status(project, expected_lock_status)
            expected_linkfiles = expected_projects[index].get('linkfiles')
            self._test_project_linkfiles(project,expected_linkfiles)

            

    def _test_project_groups(self,project,expected_groups=None):
        if expected_groups:
            error_string = 'Project groups were [{groups}], expected [{expected_groups}]'.format(groups=project.groups, expected_groups=expected_groups)
            self.assertEqual(project.groups,expected_groups,error_string)
        else:
            self.assertIsNone(project.groups,'Project groups were [{groups}], expected None'.format(groups=project.groups))

    def _test_project_names(self,project, expected_name=None):
        if expected_name:
            error_string = 'Project name was [{name}], expected [{expected_name}]'.format(name=project.name, expected_name=expected_name)
            self.assertEqual(project.name,expected_name, error_string)
        else:
            self.assertIsNone(project.name,'Project name was [{name}], expected None'.format(name=project.name))

    def _test_project_path(self, project,expected_path):
        if expected_path:
            error_string = 'Project path was [{path}], expected [{expected_path}]'.format(path=project.path, expected_path=expected_path)
            self.assertEqual(project.path, expected_path, error_string)
        else:
            self.assertIsNone(project.path,'Project path was [{path}], expected None'.format(path=project.path))

    def _test_project_revision(self, project, expected_revision):
        if expected_revision:
            error_string = 'Project revision was [{revision}], expected [{expected_revision}]'.format(revision=project.revision, expected_revision=expected_revision)
            self.assertEqual(project.revision, expected_revision, error_string)
        else:
            self.assertIsNone(project.revision,'Project revision was [{revision}], expected None'.format(revision=project.revision))

    def _test_project_alternative_develop(self, project, expected_develop):
        if expected_develop:
            error_string = 'Project alternative_develop was [{alternative}], expected [{expected_develop}]'.format(alternative=project.alternative_develop, expected_develop=expected_develop)
            self.assertEqual(project.alternative_develop, expected_develop, error_string)
        else:
            self.assertIsNone(project.alternative_develop,'Project alternative_develop was [{alternative_develop}], expected None'.format(alternative_develop=project.alternative_develop))

    def _test_project_alternative_master(self, project, expected_master):
        if expected_master:
            error_string = 'Project revision was [{alternative}], expected [{expected_master}]'.format(alternative=project.alternative_master, expected_master=expected_master)
            self.assertEqual(project.alternative_master, expected_master, error_string)
        else:
            self.assertIsNone(project.alternative_master,'Project name was [{alternative_master}], expected None'.format(alternative_master=project.alternative_master))

    def _test_project_lock_status(self, project, expected_lock_status):
        if expected_lock_status:
            error_string = 'Project lock_status was [{lock_status}], expected [{expected_lock_status}]'.format(lock_status=project.lock_status, expected_lock_status= expected_lock_status)
            self.assertEqual(project.lock_status, expected_lock_status, error_string)
        else:
            self.assertIsNone(project.lock_status,'Project lock_status was [{lock_status}], expected None'.format(lock_status=project.lock_status))

    def _test_project_linkfiles(self, project, expected_linkfiles):
        if project.search_children('linkfile'):
            link_file_amt = len(project.search_children('linkfile'))
        else:
            link_file_amt = None
        if expected_linkfiles:
            error_string = 'Project had [{len_linkfiles}], expected only {expected_linkfiles}'.format(len_linkfiles=link_file_amt, expected_linkfiles=expected_linkfiles)
            self.assertEqual(link_file_amt, expected_linkfiles, error_string), 
        else:
            self.assertIsNone(link_file_amt,'Project had {len_linkfiles}, expected None'.format(len_linkfiles=link_file_amt))

    def test_default(self):
        default = self._manifest.default
        self.assertIsInstance(default,ManifestElementInterface,'Expected ManifestElementInterface return for default element of manifest')
        self.assertEqual(default.remote,'external','Expected default remote to be set as external')
        self.assertIsNone(default.error,'Expect nothing set for error variable in default element')
        try:
            project_a = self._manifest.get_project_by_path('dira')
            self.assertEqual(project_a.remote,default.remote,'Expect project a to use default remote as none is explicitely set')
        except AttributeError as e:
            self.fail(' '.join(e.args))

    def test_git_flow(self):
        git_flow = self._manifest.git_flow
        self.assertIsInstance(git_flow,ManifestElementInterface,'Expected ManifestElementInterface return for git-flow element of manifest')
        self.assertEqual(git_flow.suffix,'v2','Expected git-flow suffix to be set to v2')
        self.assertIsNone(git_flow.error,'Expected None for error variable in git-flow element')

    def test_post_sync_scripts(self):
        post_sync_scripts = self._manifest.post_sync_scripts
        expected_post_sync_scripts = self._expected_manifest_values.get('post_sync_scripts')
        for index, post_sync_script in enumerate(post_sync_scripts):
            error_string = 'Expected {expected} in post sync path. Got [{path}]'.format(expected=expected_post_sync_scripts[index].get('path'), path=post_sync_script.path)
            self.assertEqual(post_sync_script.path,expected_post_sync_scripts[index].get('path'),error_string)

class IncludeTester(ManifestParserTester):
    def setUp(self):
        self._manifest = ScManifest(Path(__file__).resolve().parent/'resources'/'include_manifest.xml')

class FromRepoRootTester(ManifestParserTester):
    def setUp(self):
        self._manifest = ScManifest.from_repo_root(Path(__file__).resolve().parent/'resources'/'mock_.repo')

if __name__ == '__main__':
    unittest.main()
