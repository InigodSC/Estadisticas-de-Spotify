import { Component, Input, OnChanges, SimpleChanges } from "@angular/core";
import { CommonModule } from "@angular/common";
import { DomSanitizer } from "@angular/platform-browser";
import {
  HttpClient,
  provideHttpClient,
  withJsonpSupport,
} from "@angular/common/http";
import { catchError, of, timeout } from "rxjs";
import { HttpClientJsonpModule } from "@angular/common/http";

@Component({
  standalone: true,
  selector: "app-info-modal",
  imports: [CommonModule, HttpClientJsonpModule],
  templateUrl: "./info-modal.component.html",
  styleUrls: ["./info-modal.component.css"],
})
export class InfoModalComponent implements OnChanges {
  @Input() visible = false;
  @Input() type: "song" | "artist" = "song";
  @Input() data: any;

  previewUrl: string | null = null;

  constructor(public sanitizer: DomSanitizer, private http: HttpClient) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes["data"] || changes["visible"]) {
      this.handleDataChange();
    }
  }

  private handleDataChange(): void {
    console.log("🟢 Modal abierto con tipo:", this.type);
    console.log("📦 Data recibida:", this.data);

    this.previewUrl = null;

    if (this.type !== "song") return;

    if (!this.data || !this.data.name || !this.data.artists?.length) {
      console.warn(
        "⚠️ No se encontró nombre o artista en los datos de la canción"
      );
      return;
    }

    const cleanTrack = this.data.name.replace(/["']/g, "").trim();
    const artistName = (
      typeof this.data.artists[0] === "string"
        ? this.data.artists[0]
        : this.data.artists[0]?.name || ""
    )
      .replace(/["']/g, "")
      .trim();

    const lowerTrackName = cleanTrack.toLowerCase();
    const lowerArtistName = artistName.toLowerCase();

    const query = `track:"${cleanTrack}" artist:"${artistName}"`;
    const deezerUrl = `https://api.deezer.com/search?q=${encodeURIComponent(
      query
    )}&output=jsonp`;

    console.log("🌐 Llamando a Deezer con título y artista:", deezerUrl);

    this.http
      .jsonp(deezerUrl, "callback")
      .pipe(
        timeout(5000),
        catchError((err) => {
          console.warn("❌ Error o timeout al llamar a Deezer:", err);
          return of(null);
        })
      )
      .subscribe((res: any) => {
        if (res?.data?.length > 0) {
          const exactMatch = res.data.find(
            (track: any) =>
              track.title.toLowerCase() === lowerTrackName &&
              track.artist?.name?.toLowerCase() === lowerArtistName
          );

          const bestMatch = exactMatch || res.data[0];
          this.previewUrl = bestMatch.preview;

          console.log(
            "✅ Preview seleccionado (título + artista):",
            this.previewUrl
          );
        } else {
          console.log(
            `⚠️ Deezer no encontró ningún resultado para ${cleanTrack} - ${artistName}`
          );
        }
      });
  }

  closeModal() {
    this.visible = false;
  }

  getSpotifyLink(): string | null {
    return this.data?.external_urls?.spotify ?? null;
  }

  get artistNames(): string {
    return this.data?.artists?.join(", ") ?? "";
  }

  openInNewTab(): void {
    const url = this.getSpotifyLink();
    if (url) {
      window.open(url, "_blank", "noopener");
    }
  }
}
