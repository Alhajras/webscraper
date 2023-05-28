import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'shortLink'
})
export class ShortLinkPipe implements PipeTransform {

  private readonly maxLinkLength = 50
  public transform (link: string): string {
    link = link.replace('https://','').replace('http://','').replace('www.', '')
    const chars = link.length
    if (chars > this.maxLinkLength) {
      return link.substring(0, this.maxLinkLength).concat('…')
    }
    return link
  }
}
