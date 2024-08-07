import {Component, Input, OnInit} from '@angular/core';
import {Template} from "src/app/models/template.model";
import {FormBuilder, FormControl, FormGroup, Validators} from "@angular/forms";
import {HttpErrorResponse} from "@angular/common/http";
import {Action} from "src/app/models/action.model";
import {ActionService} from "src/app/services/action.service";
import {MessageService} from "primeng/api";


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
  public beforeActions: Action[] = []
  public afterActions: Action[] = []
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
  public disableActions!: FormControl

  public constructor(
    private readonly fb: FormBuilder,
    private readonly actionService: ActionService,
    private readonly messageService: MessageService
  ) {

  }

  public disableActionsChain(): void {
    this.actionService.disableActionsChain(this.template.action_chain).subscribe(() => {
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Actions status is changed!`
      });
    })
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
      disabled: this.disableActions.value,
      type: this.type.value.value,
      action_chain: this.template.action_chain,
    }
    if (this.updatedAction !== null) {
      this.addActionTypeAttributes(action)
      this.actionService.update(this.updatedAction.id, action).toPromise().then(() => {
        this.actionService.list({template: this.template.id}).subscribe(actions => {
          this.beforeActions = actions.filter(ac => ac.action_chain === this.template.action_chain)
        })
        this.closeModal()
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: `Action ${this.name.value} is edited!`
        });
        this.currentlySubmitting = false
        this.updatedAction = null
      }).catch((err: HttpErrorResponse) => {
        this.errorMessage = err.error
        this.currentlySubmitting = false
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: `Action ${this.name.value} failed to be edited!`
        });
        console.log(err)
      })
      return;
    }
    this.addActionTypeAttributes(action)
    this.actionService.post(action).toPromise().then(() => {
      this.actionService.list({template: this.template.id}).subscribe(actions => {
        this.beforeActions = actions.filter(ac => ac.action_chain === this.template.action_chain)
      })
      this.closeModal()
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Action ${this.name.value} is created!`
      });
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      this.messageService.add({
        severity: 'error',
        summary: 'Error',
        detail: `Action ${this.name.value} failed to be created!`
      });
      console.log(err)
    })
  }

  public deleteAction(action: Action): void {
    action.deleted = true
    this.actionService.update(action.id, action).toPromise().then(() => {
      this.actionService.list().subscribe(actions => {
        this.beforeActions = actions.filter(ac => ac.action_chain === this.template.action_chain)
      })
      this.closeModal()
      this.messageService.add({
        severity: 'success',
        summary: 'Success',
        detail: `Action ${action.name} is deleted!`
      });
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editAction(action: any): void {
    this.updatedAction = this.evaluateType(action)
    this.name = this.fb.control(action.name, [Validators.required])
    this.order = this.fb.control(action.order, [Validators.required])
    this.disableActions = this.fb.control(action.disabled)
    this.type = this.fb.control({key: action.type, value: action.type}, [Validators.required])
    this.selector = this.fb.control(action.selector ?? '')
    this.times = this.fb.control(action.times ?? 1)
    this.direction = this.fb.control(action.direction ?? 'down')
    this.time = this.fb.control(action.time ?? 0)
    this.form = this.fb.group({
      order: this.order,
      type: this.type,
      name: this.name,
      disabled: this.disableActions,
    })
    this.displayModal = true
  }

  public ngOnInit(): void {
    this.actionService.list({template: this.template.id}).subscribe(actions => {
      this.beforeActions = actions.filter(ac => ac.action_chain === this.template.action_chain)
    })
    this.initForm()
  }

  public createAction(): void {
    this.initForm()
    this.updatedAction = null
    this.displayModal = true
  }

  private initForm(): void {
    this.order = this.fb.control('', [Validators.required])
    this.disableActions = this.fb.control(this.template.action_chain_disabled)
    this.name = this.fb.control('', [Validators.required])
    this.type = this.fb.control('', [Validators.required])
    this.selector = this.fb.control('')
    this.times = this.fb.control('')
    this.direction = this.fb.control('')
    this.time = this.fb.control('')
    this.form = this.fb.group({
      order: this.order,
      type: this.type,
      disabled: this.disableActions,
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
    action.action_chain = this.template.action_chain
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
