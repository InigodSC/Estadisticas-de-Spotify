import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { ArtistasComponent } from './components/artistas/artistas.component';
import { CancionesComponent } from './components/canciones/canciones.component';
import { PerfilComponent } from './components/perfil/perfil.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'artistas', component: ArtistasComponent },
  { path: 'canciones', component: CancionesComponent },
  { path: 'perfil', component: PerfilComponent },
  { path: '**', redirectTo: '' }
];
