import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { BaseComponent } from './base/base.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import { BrowserModule } from '@angular/platform-browser';
import { InputFieldComponent } from './shared/input-field/input-field.component';
import { NgModule } from '@angular/core';
import { CrawlerComponent } from 'src/app/base/crawler/crawler.component';
import { TimeAgoComponent } from './shared/time-ago/time-ago.component';
import {ButtonModule} from "primeng/button";
import {CardModule} from "primeng/card";
import {DialogModule} from "primeng/dialog";
import {DropdownModule} from "primeng/dropdown";
import {HttpClientModule} from "@angular/common/http";
import {InputTextModule} from "primeng/inputtext";
import {InputTextareaModule} from "primeng/inputtextarea";
import {MenuModule} from "primeng/menu";
import {MessageModule} from "primeng/message";
import {ReactiveFormsModule} from "@angular/forms";
import {RippleModule} from "primeng/ripple";
import {TableModule} from "primeng/table";
import {TimeagoPipe} from "src/app/shared/pipes/timeago.pipe";
import {TemplateComponent} from "src/app/base/template/template.component";
import {TreeTableModule} from "primeng/treetable";
import { InspectorComponent } from './base/inspector/inspector.component';
import { RunnerComponent } from './base/runner/runner.component';
@NgModule({
  declarations: [
    AppComponent,
    BaseComponent,
    CrawlerComponent,
    TemplateComponent,
    InputFieldComponent,
    TimeAgoComponent,
    TimeagoPipe,
    InspectorComponent,
    RunnerComponent
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
    RippleModule,
    TreeTableModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
