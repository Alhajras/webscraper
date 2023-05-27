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
  public attribute!: FormControl
  public form!: FormGroup
  public header = 'Action form'
  public name!: FormControl
  public errorMessage = ''
  public templates = []
  public readonly columnCount = 8

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
      selector: this.order.value,
      attribute: this.attribute.value === '' ? null : this.attribute.value,
      template: this.template.id,
    }
    if (this.updatedAction !== null) {
      this.actionService.update(this.updatedAction.id, action).toPromise().then(() => {
        this.actionService.list({template: this.template.id}).subscribe(action => {
          // this.action = action
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
    this.actionService.post(action).toPromise().then(() => {
      this.actionService.list({template: this.template.id}).subscribe(action => {
        // this.action = action
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
    // action.deleted = true
    this.actionService.update(action.id, action).toPromise().then(() => {
      this.actionService.list().subscribe(actions => {
        // this.actions = actions
      })
      this.closeModal()
      this.currentlySubmitting = false
    }).catch((err: HttpErrorResponse) => {
      this.errorMessage = err.error
      this.currentlySubmitting = false
      console.log(err)
    })
  }

  public editAction(action: Action): void {
    this.updatedAction = action
    this.name = this.fb.control(action.name)
    this.order = this.fb.control(action.order)
    this.type = this.fb.control({key:action.type, value:action.type })
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
    this.form = this.fb.group({
      order: this.order,
      type: this.type,
      name: this.name,
    })
  }
}
