import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MenuComponent } from '../menu/menu.component';
import { OpcionesUsuarioComponent } from '../opciones-usuario/opciones-usuario.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule, MenuComponent, OpcionesUsuarioComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  showMenu = false;
  showUserOptions = false;

  despligueMenu (): void {
    this.showMenu = !this.showMenu;
  }

  toggleUserOptions(): void {
    this.showUserOptions = !this.showUserOptions;
  }
}
