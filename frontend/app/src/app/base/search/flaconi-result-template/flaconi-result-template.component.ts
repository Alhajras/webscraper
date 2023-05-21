import {Component, Input} from '@angular/core';
import {Product} from "src/app/base/search/search.component";

@Component({
  selector: 'app-flaconi-result-template',
  templateUrl: './flaconi-result-template.component.html',
  styleUrls: ['./flaconi-result-template.component.scss']
})
export class FlaconiResultTemplateComponent {
  @Input()
  product!: Product

  @Input()
  searchText = ''
}
