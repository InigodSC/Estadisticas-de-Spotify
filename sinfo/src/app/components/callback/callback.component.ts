import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-callback',
  standalone: true,
  templateUrl: './callback.component.html'
})
export class CallbackComponent implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private platformId = inject(PLATFORM_ID);

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return; // Estamos en SSR, no usamos localStorage
    }

    const token = this.route.snapshot.queryParamMap.get('access_token');

    if (token) {
      localStorage.setItem('access_token', token);
      this.router.navigate(['/home']);
    } else {
      this.router.navigate(['/login']);
    }
  }
}
