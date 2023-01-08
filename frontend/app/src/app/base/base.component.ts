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
    {label: 'Spiders', url: 'spiders'},
    {label: 'Templates', url: 'templates'}
  ]
}
