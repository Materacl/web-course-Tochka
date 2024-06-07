import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from fastui import FastUI, AnyComponent, components as c
from fastui.auth import AuthRedirect
from fastui.events import AuthEvent, GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, EmailStr, Field, SecretStr
import httpx

from .auth_user import User
from .shared import demo_page

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/api/v1/auth/token")


@router.get('/login', response_model=FastUI, response_model_exclude_none=True)
async def auth_login(user: User = Depends(User.from_request_opt)) -> list[AnyComponent]:
    if user is not None:
        raise AuthRedirect('/auth/profile')

    return demo_page(
        c.ServerLoad(
            path='/auth/login/content',
            load_trigger=PageEvent(name='tab'),
            components=auth_login_content(),
        ),
        title='Authentication',
    )


@router.get('/login/content/', response_model=FastUI, response_model_exclude_none=True)
def auth_login_content() -> list[AnyComponent]:
    return [
        c.ModelForm(model=LoginForm, submit_url='/api/auth/login', display_mode='page'),
    ]


class LoginForm(BaseModel):
    email: EmailStr = Field(
        title='Email Address', description='Enter your email', json_schema_extra={'autocomplete': 'email'}
    )
    password: SecretStr = Field(
        title='Password',
        description='Enter your password',
        json_schema_extra={'autocomplete': 'current-password'},
    )


@router.post('/login', response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(form: Annotated[LoginForm, fastui_form(LoginForm)]) -> list[AnyComponent]:
    try:
        token = await User.fetch_token(form.email, form.password.get_secret_value())
        return [c.FireEvent(event=AuthEvent(token=token, url='/auth/profile'))]
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get('/profile', response_model=FastUI, response_model_exclude_none=True)
async def profile(user: User = Depends(User.from_request)) -> list[AnyComponent]:
    return demo_page(
        c.Paragraph(text=f'You are logged in as "{user.email}".'),
        c.Button(text='Logout', on_click=PageEvent(name='submit-form')),
        c.Heading(text='User Data:', level=3),
        c.Code(language='json', text=json.dumps(user.dict(), indent=2)),
        c.Form(
            submit_url='/auth/logout',
            form_fields=[c.FormFieldInput(name='token', title='', html_type='hidden')],
            footer=[],
            submit_trigger=PageEvent(name='submit-form'),
        ),
        title='Authentication',
    )


@router.post('/logout', response_model=FastUI, response_model_exclude_none=True)
async def logout_form_post() -> list[AnyComponent]:
    return [c.FireEvent(event=AuthEvent(token=False, url='/auth/login'))]
