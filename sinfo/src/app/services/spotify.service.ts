import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class SpotifyService {
  //http://81.34.225.171:15705
  private readonly baseUrl = "http://localhost:8888";
  constructor(private http: HttpClient) {}

  getUserName(token: string): Observable<{ nombre: string }> {
    return this.http.get<{ nombre: string }>(
      `${this.baseUrl}/usr_name/${token}`
    );
  }
  getUserPic(token: string): Observable<{ url: string }> {
    return this.http.get<{ url: string }>(`${this.baseUrl}/usr_pic/${token}`);
  }
  getCountry(token: string): Observable<{ country: string }> {
    return this.http.get<{ country: string }>(
      `${this.baseUrl}/usr_country/${token}`
    );
  }
  getEmail(token: string): Observable<{ email: string }> {
    return this.http.get<{ email: string }>(
      `${this.baseUrl}/usr_email/${token}`
    );
  }
  getFollowers(token: string): Observable<{ followers: string }> {
    return this.http.get<{ followers: string }>(
      `${this.baseUrl}/usr_followers/${token}`
    );
  }
  getTopArtists(token: string, n: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_artists/${token}?limit=${n}`);
  }
  getTopTracks(token: string, n: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/top_tracks/${token}?limit=${n}`);
  }
  getTopTracksRange(
    token: string,
    limit: number,
    timeRange: string = "long_term"
  ) {
    return this.http.get<any[]>(`${this.baseUrl}/top_tracks/${token}`, {
      params: {
        limit: limit.toString(),
        time_range: timeRange,
      },
    });
  }

  getRecentTracks(token: string, n: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/recent_tracks/${token}?limit=${n}`);
  }
  getRecommendTracksById(token: string, trackId: string): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/recommend_tracks/${token}/${trackId}`
    );
  }
  getRecommendArtistsById(token: string, artistId: string): Observable<any[]> {
    return this.http.get<any[]>(
      `${this.baseUrl}/recommend_artists/${token}/${artistId}`
    );
  }
  getCustomRecommendations(token: string): Observable<any[]> {
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
    });
    return this.http.get<any[]>(`${this.baseUrl}/recommend_custom`, {
      headers,
    });
  }
  getCustomArtistRecommendations(token: string): Observable<any[]> {
  const headers = new HttpHeaders({
    Authorization: `Bearer ${token}`
  });
  return this.http.get<any[]>(`${this.baseUrl}/recommend_artists_custom`, { headers });
}

  getToken(): Observable<any> {
    return this.http.get(`${this.baseUrl}/token`);
  }
  logout(): void {
    localStorage.removeItem("access_token");
  }
}
