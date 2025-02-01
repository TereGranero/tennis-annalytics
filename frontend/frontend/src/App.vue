<template>
  <div class="app">
    <div class="row align-items-center">
      <div class="col-md-4">
        <img 
            src="../public/images/tennis-analytics.png" 
            alt="Tennis Analytics Logo" 
            class="img-fluid mb-3" 
            style="max-width: 100%; height: auto; border-radius: 10px;"
        />
      </div>

      <!-- Navigation menu -->
      <div class="col-md-8">
        <nav class="navbar navbar-expand-md navbar-light bg-white">
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navBarMenu"
            aria-controls="navbarMenu"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
          <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navBarMenu">
            <ul class="navbar-nav ms-auto">
              <li class="nav-item">
                <router-link to="/players" class="nav-link">Jugadores</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/rankings" class="nav-link">Rankings</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/tournaments" class="nav-link">Torneos</router-link>
              </li>
            </ul>
          </div>
        </nav> 
      </div>
    </div>

    <router-view />
  </div>
</template>

<style>
#app {
  margin-top: 5px;
}
</style>
