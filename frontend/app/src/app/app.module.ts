import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BaseComponent } from './base/base.component';
import {MenuModule} from "primeng/menu";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import {TableModule} from "primeng/table";
import {HttpClientModule} from "@angular/common/http";
import { SpiderComponent } from 'src/app/base/spider/spider.component';
import {DialogModule} from "primeng/dialog";
import {CardModule} from "primeng/card";
import {DropdownModule} from "primeng/dropdown";
import {MessageModule} from "primeng/message";
import {ReactiveFormsModule} from "@angular/forms";
import {InputTextareaModule} from "primeng/inputtextarea";
import {InputTextModule} from "primeng/inputtext";
import {ButtonModule} from "primeng/button";
import {RippleModule} from "primeng/ripple";
import { InputFieldComponent } from './shared/input-field/input-field.component';
@NgModule({
  declarations: [
    AppComponent,
    BaseComponent,
    SpiderComponent,
    InputFieldComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MenuModule,
    BrowserAnimationsModule,
    TableModule,
    HttpClientModule,
    DialogModule,
    CardModule,
    DropdownModule,
    MessageModule,
    ReactiveFormsModule,
    InputTextareaModule,
    InputTextModule,
    ButtonModule,
    RippleModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
