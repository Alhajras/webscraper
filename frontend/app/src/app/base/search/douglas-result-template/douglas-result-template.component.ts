import {Component, Input} from '@angular/core';
import {Product} from "src/app/base/search/search.component";

@Component({
  selector: 'app-douglas-result-template',
  templateUrl: './douglas-result-template.component.html',
  styleUrls: ['./douglas-result-template.component.scss']
})
export class DouglasResultTemplateComponent {
  @Input()
  product!: Product

  @Input()
  searchText = ''
}
