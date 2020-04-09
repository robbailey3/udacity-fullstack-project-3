import { environment } from '../../environments/environment';
import { Injectable } from '@angular/core';
import { JwtHelperService } from '@auth0/angular-jwt';

const JWTS_LOCAL_KEY = 'JWTS_LOCAL_KEY';
const JWTS_ACTIVE_INDEX_KEY = 'JWTS_ACTIVE_INDEX_KEY';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  url = environment.auth0.url;
  audience = environment.auth0.audience;
  clientId = environment.auth0.clientId;
  callbackURL = environment.auth0.callbackURL;

  token: string;
  payload: any;

  constructor() {}

  public buildLoginLink(callbackPath = '') {
    let link = 'https://';
    link += this.url + '.auth0.com';
    link += '/authorize?';
    link += 'audience=' + this.audience + '&';
    link += 'response_type=token&';
    link += 'client_id=' + this.clientId + '&';
    link += 'redirect_uri=' + this.callbackURL + callbackPath;
    return link;
  }

  // invoked in app.component on load
  public checkTokenFragment() {
    // parse the fragment
    const fragment = window.location.hash.substr(1).split('&')[0].split('=');
    // check if the fragment includes the access token
    if (fragment[0] === 'access_token') {
      // add the access token to the jwt
      this.token = fragment[1];
      // save jwts to localstore
      this.setJWT();
    }
  }

  public setJWT() {
    localStorage.setItem(JWTS_LOCAL_KEY, this.token);
    if (this.token) {
      this.decodeJWT(this.token);
    }
  }

  public loadJwts() {
    this.token = localStorage.getItem(JWTS_LOCAL_KEY) || null;
    if (this.token) {
      this.decodeJWT(this.token);
    }
  }

  public activeJWT() {
    return this.token;
  }

  public decodeJWT(token: string) {
    const jwtservice = new JwtHelperService();
    this.payload = jwtservice.decodeToken(token);
    return this.payload;
  }

  public logout() {
    this.token = '';
    this.payload = null;
    this.setJWT();
  }

  public can(permission: string) {
    return (
      this.payload &&
      this.payload.permissions &&
      this.payload.permissions.length &&
      this.payload.permissions.indexOf(permission) >= 0
    );
  }
}
