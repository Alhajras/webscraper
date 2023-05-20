import { Component, Input, OnInit } from '@angular/core'

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

  public ngOnInit (): void {
    if (this.searchString === '') {
      this.innerHtml = this.text
      return
    }
    const regex = new RegExp(this.searchString, 'gi')
    this.innerHtml = this.text
      .replace(regex, matchStr => '<mark>' + matchStr + '</mark>')
  }
}
