import {Component} from '@angular/core';
import {MenuItem} from "primeng/api";
import {SpiderService} from "src/app/services/spider.service";
import {Spider} from "src/app/models/spider.model";

@Component({
  selector: 'app-base',
  templateUrl: './base.component.html',
  styleUrls: ['./base.component.scss']
})
export class BaseComponent {
  public items: MenuItem[] = [
    {label: 'Spiders'},
    {label: 'Templates'},
    {label: 'Runners'}
  ]
  public spiders: Spider[] = []

  public constructor(private readonly spiderService: SpiderService) {
    spiderService.list().subscribe(spiders => {
      this.spiders = spiders
    })
  }

}
