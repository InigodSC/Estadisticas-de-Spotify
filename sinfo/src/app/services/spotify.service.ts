import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {

  private readonly baseUrl = 'http://localhost:8888';
  constructor(private http: HttpClient) {}

  getUserName(token:string): Observable<{ nombre: string }> {
    return this.http.get<{ nombre: string }>(`${this.baseUrl}/usr_name/${token}`);
  } 
  getUserPic(token:string): Observable<{ url: string }> {
    return this.http.get<{ url: string }>(`${this.baseUrl}/usr_pic/${token}`);
  }
  getCountry(token:string):Observable<{country:string}>{
    return this.http.get<{country:string}>(`${this.baseUrl}/usr_country/${token}`);
  }
  getEmail(token:string):Observable<{email:string}>{
    return this.http.get<{email:string}>(`${this.baseUrl}/usr_email/${token}`);
  }
  getFollowers(token:string):Observable<{followers:string}>{
    return this.http.get<{followers:string}>(`${this.baseUrl}/usr_followers/${token}`);
  }
  getTopArtists(token:string, n:number): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_artists/${token}?limit=${n}`);
  }
  getTopTracks(token:string, n:number): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_tracks/${token}?limit=${n}`);
  }
  getRecentTracks(token:String, n:number): Observable<any>{
    return this.http.get(`${this.baseUrl}/recent_tracks/${token}?limit=${n}`);
  }
  getToken(): Observable<any> {
    return this.http.get(`${this.baseUrl}/token`);
  }
  logout(): void {
    localStorage.removeItem('access_token');
  }

}
