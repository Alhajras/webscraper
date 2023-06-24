import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'shortText'
})
export class ShortTextPipe implements PipeTransform {

  private readonly maxLinkLength = 250
  public transform (link: string): string {
    const chars = link.length
    if (chars > this.maxLinkLength) {
      return link.substring(0, this.maxLinkLength).concat('…')
    }
    return link
  }
}
