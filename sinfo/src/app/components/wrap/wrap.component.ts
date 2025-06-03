import { Component, OnInit, Inject, PLATFORM_ID, inject } from "@angular/core";
import { isPlatformBrowser } from "@angular/common";
import { SpotifyService } from "../../services/spotify.service";
import { CommonModule } from "@angular/common";
import { Router } from "@angular/router";

@Component({
  selector: "app-wrap",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./wrap.component.html",
  styleUrls: ["./wrap.component.css"],
})
export class WrapComponent implements OnInit {
  private router = inject(Router);
  stats: {
    tiempo: number;
    generos: { nombre: string; porcentaje: number }[];
  }[] = [
    { tiempo: 0, generos: [] },
    { tiempo: 0, generos: [] },
    { tiempo: 0, generos: [] },
  ];
  currentSlide = 0;

  constructor(
    private spotifyService: SpotifyService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem("access_token");
    if (!token) return;

    this.spotifyService.getWrapStatsLong(token).subscribe({
      next: (res) => {
        console.log("long_term OK", res);
        this.stats = [
          {
            tiempo: res.tiempo_escuchado_min,
            generos: res.generos,
          },
          this.stats[1],
          this.stats[2],
        ];
      },
      error: (err) => console.error("Error long_term", err),
    });

    this.spotifyService.getWrapStatsMedium(token).subscribe({
      next: (res) => {
        console.log("medium_term OK", res);
        this.stats = [
          this.stats[0],
          {
            tiempo: res.tiempo_escuchado_min,
            generos: res.generos,
          },
          this.stats[2],
        ];
      },
      error: (err) => console.error("Error medium_term", err),
    });

    this.spotifyService.getWrapStatsShort(token).subscribe({
      next: (res) => {
        console.log("short_term OK", res);
        this.stats = [
          this.stats[0],
          this.stats[1],
          {
            tiempo: res.tiempo_escuchado_min,
            generos: res.generos,
          },
        ];
      },
      error: (err) => console.error("Error short_term", err),
    });
  }

  prevSlide(): void {
    if (this.currentSlide > 0) this.currentSlide--;
  }

  nextSlide(): void {
    if (this.currentSlide < this.stats.length - 1) this.currentSlide++;
  }

  volver():void{
    this.router.navigate(['/']);
  }
}
