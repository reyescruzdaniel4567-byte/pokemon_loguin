from django.conf import settings
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Pokemon, Entrenador, Gimnasio
import folium


@login_required
@permission_required('visual.view_pokemon', raise_exception=True)
def home(request):
    pokemons = Pokemon.objects.all()
    entrenadores = Entrenador.objects.all()
    gimnasios = Gimnasio.objects.all()

    coordenadas_inicio = [4.5981, -74.1297]

    mapa = folium.Map(
        location=coordenadas_inicio,
        zoom_start=14,
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Street_Map/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, and others",
    )

    for gym in gimnasios:
        if gym.latitud is not None and gym.longitud is not None:
            popup_contenido = f"""
            <div style="font-family: Arial;">
                <h3>Gimnasio {gym.naturaleza_del_gym}</h3>
                <p>
                    <b>Líder:</b>
                    {gym.lider_del_gym.nombre}
                    {gym.lider_del_gym.apellido}
                </p>
                <p>
                    <b>Medallas:</b> {gym.medallas}
                </p>
            </div>
            """

            folium.Marker(
                location=[gym.latitud, gym.longitud],
                popup=folium.Popup(popup_contenido, max_width=250),
                tooltip=f"Gimnasio {gym.naturaleza_del_gym}",
                icon=folium.Icon(color="red", icon="star")
            ).add_to(mapa)

    mapa_html = mapa._repr_html_()

    contexto = {
        'pokemons': pokemons,
        'entrenadores': entrenadores,
        'gimnasios': gimnasios,
        'mapa': mapa_html,
    }

    return render(request, 'visual/index.html', contexto)


@login_required
@permission_required('visual.view_pokemon', raise_exception=True)
def buscar(request):
    q = request.GET.get('q', '').strip()
    pokemons = []
    buscado = False

    if q:
        buscado = True
        pokemons = Pokemon.objects.filter(nombre__icontains=q).select_related('entrenador')

    return render(request, 'visual/buscar.html', {
        'q': q,
        'pokemons': pokemons,
        'buscado': buscado,
    })


class AdminRequeridoMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


class FormularioMixin(AdminRequeridoMixin):
    template_name = 'visual/form.html'
    success_url = reverse_lazy('home')
    fields = '__all__'


class EliminarMixin(AdminRequeridoMixin):
    template_name = 'visual/confirmar_eliminar.html'
    success_url = reverse_lazy('home')


# --- POKEMON ---
class PokemonCrear(FormularioMixin, CreateView):
    model = Pokemon
    permission_required = 'visual.add_pokemon'
    extra_context = {'titulo': 'Nuevo Pokémon'}


class PokemonEditar(FormularioMixin, UpdateView):
    model = Pokemon
    permission_required = 'visual.change_pokemon'
    extra_context = {'titulo': 'Editar Pokémon'}


class PokemonEliminar(EliminarMixin, DeleteView):
    model = Pokemon
    permission_required = 'visual.delete_pokemon'


# --- ENTRENADOR ---
class EntrenadorCrear(FormularioMixin, CreateView):
    model = Entrenador
    permission_required = 'visual.add_entrenador'
    extra_context = {'titulo': 'Nuevo Entrenador'}


class EntrenadorEditar(FormularioMixin, UpdateView):
    model = Entrenador
    permission_required = 'visual.change_entrenador'
    extra_context = {'titulo': 'Editar Entrenador'}


class EntrenadorEliminar(EliminarMixin, DeleteView):
    model = Entrenador
    permission_required = 'visual.delete_entrenador'


# --- GIMNASIO ---
class GimnasioCrear(FormularioMixin, CreateView):
    model = Gimnasio
    permission_required = 'visual.add_gimnasio'
    extra_context = {'titulo': 'Nuevo Gimnasio'}


class GimnasioEditar(FormularioMixin, UpdateView):
    model = Gimnasio
    permission_required = 'visual.change_gimnasio'
    extra_context = {'titulo': 'Editar Gimnasio'}


class GimnasioEliminar(EliminarMixin, DeleteView):
    model = Gimnasio
    permission_required = 'visual.delete_gimnasio'
