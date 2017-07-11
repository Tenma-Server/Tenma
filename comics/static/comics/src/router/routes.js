import Main from '@/components/layout/Main'
import ArcDetail from '@/components/arc/ArcDetail'
import CharacterDetail from '../components/character/CharacterDetail'
import IssueDetail from '@/components/issue/IssueDetail'
import PublisherDetail from '@/components/publisher/PublisherDetail'
import SeriesDetail from '@/components/series/SeriesDetail'
import Settings from '@/components/Settings'
import TeamDetail from '@/components/team/TeamDetail'
import Viewer from '@/components/Viewer'

export const routes = [
	{ path: '/', component: Main, name: 'Home' },
	{ path: '/arc/:id', component: ArcDetail, name: 'Arc' },
	{ path: '/character/:id', component: CharacterDetail, name: 'Character' },
	{ path: '/issue/:id', component: IssueDetail, name: 'Issue' },
	{ path: '/issue/:id/read', component: Viewer, name: 'Viewer' },
	{ path: '/publisher/:id', component: PublisherDetail, name: 'Publisher' },
	{ path: '/series/:id', component: SeriesDetail, name: 'Series' },
	{ path: '/settings', component: Settings, name: 'Settings' },
	{ path: '/team/:id', component: TeamDetail, name: 'Team' }
]
