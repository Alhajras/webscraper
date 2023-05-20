import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";

@Component({
  selector: 'app-base',
  templateUrl: './base.component.html',
  styleUrls: ['./base.component.scss']
})
export class BaseComponent {
  public items: MenuItem[] = [
    {label: 'Runners', url: 'runners'},
    {label: 'Crawlers', url: 'crawlers'},
    {label: 'Templates', url: 'templates'},
    {label: 'Indexers', url: 'indexers'},
    {label: 'Search', url: 'search'}
  ]
}
