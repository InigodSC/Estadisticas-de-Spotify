import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {

  private readonly baseUrl = 'http://localhost:8888';

  constructor(private http: HttpClient) {}

  getUserName(): Observable<{ nombre: string }> {
    return this.http.get<{ nombre: string }>(`${this.baseUrl}/usr_name`);
  } 
  getUserPic(): Observable<{ url: string }> {
    return this.http.get<{ url: string }>(`${this.baseUrl}/usr_pic`);
  }
  getTopArtists(): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_artists?limit=10`);
  }
  getTopTracks(): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_tracks?limit=10`);
  }
  getRecentTracks(): Observable<any>{
    return this.http.get(`${this.baseUrl}/recent_tracks?limit=10`);
  }
  getToken(): Observable<any> {
    return this.http.get(`${this.baseUrl}/token`);
  }
}
