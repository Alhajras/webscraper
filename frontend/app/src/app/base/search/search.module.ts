import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { SearchRoutingModule } from 'src/app/base/search/search-routing.module';
import {ButtonModule} from "primeng/button";


@NgModule({
  declarations: [
  ],
  exports: [
  ],
  imports: [
    CommonModule,
    SearchRoutingModule,
    ButtonModule
  ]
})
export class SearchModule { }
