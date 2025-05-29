import { Component, Input } from "@angular/core";
import { CommonModule } from "@angular/common";
import { DomSanitizer } from "@angular/platform-browser";

@Component({
  standalone: true,
  selector: "app-info-modal",
  imports: [CommonModule],
  templateUrl: "./info-modal.component.html",
  styleUrls: ["./info-modal.component.css"],
})
export class InfoModalComponent {
  @Input() visible = false;
  @Input() type: "song" | "artist" = "song";
  @Input() data: any;

  constructor(public sanitizer: DomSanitizer) {}

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
