import {Component, Input, OnInit} from '@angular/core'

@Component({
  selector: 'app-marked-text',
  templateUrl: './marked-text.component.html',
  styleUrls: ['./marked-text.component.scss'],
})
export class MarkedTextComponent implements OnInit {
  @Input()
  public text!: string

  @Input()
  public searchString!: string

  public innerHtml!: string

  public ngOnInit(): void {
    if (this.searchString === '') {
      this.innerHtml = this.text
      return
    }
    let result = this.text
    this.searchString.trim().split(' ').forEach(w => {
      const regex = new RegExp(w, 'gi')
      result = result
        .replace(regex, matchStr => '<mark>' + matchStr + '</mark>')

    })
    this.innerHtml = result
  }
}
