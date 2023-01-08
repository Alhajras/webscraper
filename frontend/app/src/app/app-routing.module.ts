import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {TemplateComponent} from "src/app/base/template/template.component";
import {SpiderComponent} from "src/app/base/spider/spider.component";
import {RunnerComponent} from "src/app/base/runner/runner.component";

const routes: Routes = [
  {
    path: 'templates',
    component: TemplateComponent,
    loadChildren: () => import('./base/template/template.module').then(m => m.TemplateModule)
  },
  {
    path: 'spiders',
    component: SpiderComponent,
    loadChildren: () => import('./base/spider/spider.module').then(m => m.SpiderModule)
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
