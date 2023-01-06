import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-time-ago',
  templateUrl: './time-ago.component.html',
  styleUrls: ['./time-ago.component.scss']
})
export class TimeAgoComponent {
  @Input()
  public time!: string

  @Input()
  public tooltipPosition: 'top' | 'bottom' | 'left' | 'right' = 'top'

}
