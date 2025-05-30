import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DeezerService {

  constructor(private http: HttpClient) {}

  searchTrackByName(name: string): Observable<any> {
    const url = `https://api.deezer.com/search?q=${encodeURIComponent(name)}&output=jsonp`;
    return this.http.jsonp(url, 'callback');  // Deezer necesita JSONP
  }
}
