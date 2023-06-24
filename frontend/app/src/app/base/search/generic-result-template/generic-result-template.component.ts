import {Component, Input} from '@angular/core';
import {Product} from "src/app/base/search/search.component";

@Component({
  selector: 'app-generic-result-template',
  templateUrl: './generic-result-template.component.html',
  styleUrls: ['./generic-result-template.component.scss']
})
export class GenericResultTemplateComponent {
  @Input()
  document!: Product

  @Input()
  searchText = ''
}
