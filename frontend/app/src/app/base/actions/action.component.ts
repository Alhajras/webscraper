import {Component, Input, OnInit} from '@angular/core';
import {Template} from "src/app/models/template.model";
import {FormBuilder, FormControl, FormGroup} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Action, ActionChain} from "src/app/models/action.model";
import {ActionService} from "src/app/services/action.service";


export interface TypeDropDown {
  key: string
  value: string
}

@Component({
  selector: 'app-action',
  templateUrl: './action.component.html',
  styleUrls: ['./action.component.scss']
})
export class ActionComponent implements OnInit {
  @Input()
  public template!: Template
  public beforeActionChain!: ActionChain
  public beforeActions: Action[] = []
  public afterActionChain!: ActionChain
  public afterActions: Action[] = []
  // public actions: Action[] = []
  public updatedAction: Action | null = null
  public type!: FormControl
  public typesList: TypeDropDown[] = [{key: 'click', value: 'click'}, {key: 'scroll', value: 'scroll'}, {
    key: 'wait',
    value: 'wait'
  }]
  public currentlySubmitting = false
  public displayModal = false
  public order!: FormControl
  public form!: FormGroup
  public header = 'Action form'
  public name!: FormControl
  public errorMessage = ''
  public templates = []
  public readonly columnCount = 4
  public selector!: FormControl
  public times!: FormControl
  public direction!: FormControl
  public time!: FormControl

  public constructor(
    private readonly fb: FormBuilder,
    private readonly actionService: ActionService,
  ) {

  }

  public closeModal(): void {
    this.displayModal = false
  }

  public submit(): void {
    if (!this.form.valid) {
      // We should normally never get here since the submit button should be disabled.
      console.warn('Form not valid.')
      return
    }

    this.currentlySubmitting = true
    const action = {
      name: this.name.value,
      order: this.order.value,
      type: this.type.value.value,
    }
    if (this.updatedAction !== null) {
      this.actionService.update(this.updatedAction.id, action).toPromise().then(() => {
        this.actionService.list({template: this.template.id}).subscribe(action => {
          this.beforeActions = action
        })
        this.closeModal()
        this.currentlySubmitting = false
        this.updatedAction = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        console.log(err)
      })
      return;
    }
    this.addActionTypeAttributes(action)
    this.actionService.post(action).toPromise().then(() => {
      this.actionService.list({template: this.template.id}).subscribe(action => {
        this.beforeActions = action
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public deleteAction(action: Action): void {
    action.deleted = true
    this.actionService.update(action.id, action).toPromise().then(() => {
      this.actionService.list().subscribe(actions => {
        this.beforeActions = actions
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editAction(action: any): void {
    this.updatedAction = this.evaluateType(action)
    this.name = this.fb.control(action.name)
    this.order = this.fb.control(action.order)
    this.type = this.fb.control({key: action.type, value: action.type})
    this.selector = this.fb.control(action.selector ?? '')
    this.times = this.fb.control(action.times ?? 1)
    this.direction = this.fb.control(action.direction ?? 'down')
    this.time = this.fb.control(action.time ?? 0)
    this.form = this.fb.group({
      order: this.order,
      type: this.type,
      name: this.name,
    })
    this.displayModal = true
  }

  public ngOnInit(): void {
    this.actionService.list({template: this.template.id}).subscribe(actions => {
      this.beforeActions = actions
    })
    this.initForm()
  }

  public createAction(): void {
    this.initForm()
    this.updatedAction = null
    this.displayModal = true
  }

  private initForm(): void {
    this.order = this.fb.control('')
    this.name = this.fb.control('')
    this.type = this.fb.control('')
    this.selector = this.fb.control('')
    this.times = this.fb.control('')
    this.direction = this.fb.control('')
    this.time = this.fb.control('')
    this.form = this.fb.group({
      order: this.order,
      type: this.type,
      name: this.name,
      selector: this.selector,
      times: this.times,
      direction: this.direction,
      time: this.time
    })
  }

  private addActionTypeAttributes(action: any): any {
    switch (action.type) {
      case 'click':
        action.selector = this.selector.value
        action.resourcetype = 'ClickAction'
        break;
      case 'scroll':
        action.times = this.times.value
        action.direction = this.direction.value
        action.resourcetype = 'ScrollAction'
        break;
      case 'wait':
        action.time = this.time.value
        action.resourcetype = 'WaitAction'
        break;
    }
    action = this.evaluateType(action)
    action.action_chain = 2
    return action
  }

  /**
   * Because action is a superclass we want to know which is the correct child class is the one we are editing
   * @param action
   * @private
   */
  private evaluateType(action: any): any {
    switch (action.type) {
      case 'click':
        action.resourcetype = 'ClickAction'
        break;
      case 'scroll':
        action.resourcetype = 'ScrollAction'
        break;
      case 'wait':
        action.resourcetype = 'WaitAction'
        break;
    }
    return action
  }
}
