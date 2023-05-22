import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {TemplateComponent} from "src/app/base/template/template.component";
import {CrawlerComponent} from "src/app/base/crawler/crawler.component";
import {RunnerComponent} from "src/app/base/runner/runner.component";
import {IndexerComponent} from "src/app/base/indexer/indexer.component";
import {SearchComponent} from "src/app/base/search/search.component";
import {DocumentationComponent} from "src/app/base/documentation/documentation.component";

const routes: Routes = [
  {
    path: 'templates',
    component: TemplateComponent,
    loadChildren: () => import('./base/template/template.module').then(m => m.TemplateModule)
  },
  {
    path: 'crawlers',
    component: CrawlerComponent,
    loadChildren: () => import('./base/crawler/crawler.module').then(m => m.CrawlerModule)
  },
  {
    path: 'runners',
    component: RunnerComponent,
    loadChildren: () => import('./base/runner/runner.module').then(m => m.RunnerModule)
  },
  {
    path: 'indexers',
    component: IndexerComponent,
    loadChildren: () => import('./base/indexer/indexer.module').then(m => m.IndexerModule)
  },
  {
    path: 'search',
    component: SearchComponent,
    loadChildren: () => import('./base/search/search.module').then(m => m.SearchModule)
  },
  {
    path: 'documentation',
    component: DocumentationComponent,
    loadChildren: () => import('./base/documentation/documentation.module').then(m => m.DocumentationModule)
  },
  {
    path: '',
    component: DocumentationComponent,
    loadChildren: () => import('./base/documentation/documentation.module').then(m => m.DocumentationModule)
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
