import {Component, Input} from '@angular/core';
import {Template} from "src/app/models/template.model";

@Component({
  selector: 'app-inspector',
  templateUrl: './inspector.component.html',
  styleUrls: ['./inspector.component.scss']
})
export class InspectorComponent {
  @Input()
  public template!: Template
}
