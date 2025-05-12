import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {

  private readonly baseUrl = 'http://localhost:8888'; // Cambia este puerto si tu backend usa otro

  constructor(private http: HttpClient) {}

  getUserName(): Observable<any> {
    return this.http.get(`${this.baseUrl}/usr_name`);
  }

  getUserPic(): Observable<any> {
    return this.http.get(`${this.baseUrl}/usr_pic`, { responseType: 'text' });
  }

  getTopArtists(): Observable<any> {
  return this.http.get(`${this.baseUrl}/top_artists?limit=10`);
  }

  getTopTracks(): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_tracks?limit=10`);
  }
}
