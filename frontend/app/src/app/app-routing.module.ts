import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {TemplateComponent} from "src/app/base/template/template.component";
import {CrawlerComponent} from "src/app/base/crawler/crawler.component";
import {RunnerComponent} from "src/app/base/runner/runner.component";

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
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
