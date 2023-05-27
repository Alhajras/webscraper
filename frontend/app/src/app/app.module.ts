import {AppComponent} from './app.component';
import {AppRoutingModule} from './app-routing.module';
import {BaseComponent} from './base/base.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations'
import {BrowserModule} from '@angular/platform-browser';
import {InputFieldComponent} from './shared/input-field/input-field.component';
import {NgModule} from '@angular/core';
import {CrawlerComponent} from 'src/app/base/crawler/crawler.component';
import {TimeAgoComponent} from './shared/time-ago/time-ago.component';
import {ButtonModule} from "primeng/button";
import {CardModule} from "primeng/card";
import {DialogModule} from "primeng/dialog";
import {DropdownModule} from "primeng/dropdown";
import {HttpClientModule} from "@angular/common/http";
import {InputTextModule} from "primeng/inputtext";
import {InputTextareaModule} from "primeng/inputtextarea";
import {MenuModule} from "primeng/menu";
import {MessageModule} from "primeng/message";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {RippleModule} from "primeng/ripple";
import {TableModule} from "primeng/table";
import {TimeagoPipe} from "src/app/shared/pipes/timeago.pipe";
import {TemplateComponent} from "src/app/base/template/template.component";
import {TreeTableModule} from "primeng/treetable";
import {InspectorComponent} from './base/inspector/inspector.component';
import {RunnerComponent} from './base/runner/runner.component';
import {IndexerComponent} from './base/indexer/indexer.component';
import {ActionComponent} from './base/actions/action.component';
import {StepsModule} from "primeng/steps";
import {TimelineModule} from "primeng/timeline";
import {ChipsModule} from "primeng/chips";
import {OverlayPanelModule} from "primeng/overlaypanel";
import {MenubarModule} from "primeng/menubar";
import {MultiSelectModule} from "primeng/multiselect";
import {SearchComponent} from "src/app/base/search/search.component";
import {DataViewModule} from "primeng/dataview";
import {RatingModule} from "primeng/rating";
import {TagModule} from "primeng/tag";
import {MarkedTextComponent} from "src/app/shared/marked-text/marked-text.component";
import {InputFieldErrorComponent} from "src/app/shared/input-field-error/input-field-error.component";
import {SearchModule} from "src/app/base/search/search.module";
import {
  FlaconiResultTemplateComponent
} from "src/app/base/search/flaconi-result-template/flaconi-result-template.component";
import {
  DouglasResultTemplateComponent
} from "src/app/base/search/douglas-result-template/douglas-result-template.component";
import { ShortLinkPipe } from './shared/pipes/short-link.pipe';
import {AccordionModule} from "primeng/accordion";
import { DocumentationComponent } from './base/documentation/documentation.component';
import {TabViewModule} from "primeng/tabview";

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
    RunnerComponent,
    IndexerComponent,
    ActionComponent,
    SearchComponent,
    MarkedTextComponent,
    InputFieldErrorComponent,
    FlaconiResultTemplateComponent,
    DouglasResultTemplateComponent,
    ShortLinkPipe,
    DocumentationComponent
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
        TreeTableModule,
        StepsModule,
        TimelineModule,
        ChipsModule,
        OverlayPanelModule,
        MenubarModule,
        MultiSelectModule,
        DataViewModule,
        RatingModule,
        TagModule,
        FormsModule,
        SearchModule,
        AccordionModule,
        TabViewModule
    ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
