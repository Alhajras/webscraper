import { Component } from '@angular/core';
import {MenuItem} from "primeng/api";

@Component({
  selector: 'app-base',
  templateUrl: './base.component.html',
  styleUrls: ['./base.component.scss']
})
export class BaseComponent {
    public items: MenuItem[] = []
    products1 = []

    ngOnInit() {
        this.items = [
            {label: 'Spiders'},
            {label: 'Templates'},
            {label: 'Runners'}
        ];
    }
}
