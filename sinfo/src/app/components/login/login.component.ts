import { Component } from '@angular/core';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  iniciarSesion(): void { //http://81.34.198.6:15705/login
    window.location.href = 'http://localhost:8888/login';
  }
}
