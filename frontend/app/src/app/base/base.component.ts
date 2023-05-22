import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";

@Component({
  selector: 'app-base',
  templateUrl: './base.component.html',
  styleUrls: ['./base.component.scss']
})
export class BaseComponent {
  public items: MenuItem[] = [
    {label: 'Documentation', url: 'documentation', icon: 'pi pi-info-circle' },
    {label: 'Runners', url: 'runners', icon: 'pi pi-send' },
    {label: 'Crawlers', url: 'crawlers', icon: 'pi pi-cloud-download'},
    {label: 'Templates', url: 'templates', icon: 'pi pi-book'},
    {label: 'Indexers', url: 'indexers', icon: 'pi pi-sitemap'},
    {label: 'Search', url: 'search', icon: 'pi pi-search'}
  ]
}
