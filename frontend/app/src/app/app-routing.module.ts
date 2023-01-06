import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {TemplateComponent} from "src/app/base/template/template.component";
import {SpiderComponent} from "src/app/base/spider/spider.component";

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
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
