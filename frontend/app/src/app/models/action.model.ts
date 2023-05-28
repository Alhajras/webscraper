export interface Action {
  id: number
  name: string
  type: string
  action_chain: number
  order: number
  deleted: boolean
}

export interface ClickAction extends Action{
  id: number
  selector: string
}

export interface WaitAction extends Action{
  id: number
  time: number
}

export interface ScrollAction extends Action{
  id: number
  times: number
  direction: string
}

export interface ActionChain {
  id: number
  name: string
  template: number
  event: string
}
