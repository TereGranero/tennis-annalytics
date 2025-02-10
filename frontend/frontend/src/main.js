import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.min.css'
import 'bootstrap/dist/css/bootstrap.css'
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'

// ECharts components
import { 
   BarChart, 
   LineChart
} from 'echarts/charts'

import { 
   TitleComponent, 
   TooltipComponent, 
   GridComponent, 
   ToolboxComponent, 
   LegendComponent 
} from 'echarts/components'

import { CanvasRenderer } from 'echarts/renderers'

use([
   BarChart,
   LineChart,
   TitleComponent, 
   TooltipComponent, 
   GridComponent, 
   ToolboxComponent,
   LegendComponent,
   CanvasRenderer
])

// Creates application
const app= createApp(App)

// Uses router
app.use(router)

// Adds v-chart component
app.component('v-chart', ECharts)

// Mounts application
app.mount("#app")
