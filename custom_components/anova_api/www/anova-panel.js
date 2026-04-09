import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class AnovaPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
      recipes: { type: Array },
      searchQuery: { type: String },
      editingRecipe: { type: Object },
    };
  }

  constructor() {
    super();
    this.recipes = [];
    this.searchQuery = "";
    this.editingRecipe = null;
  }

  firstUpdated() {
    this._fetchRecipes();
  }

  async _fetchRecipes() {
    // In a real integration, we'd add an endpoint or a websocket command to fetch storage.
    // For now, we simulate fetching since standard frontend panels usually require a dedicated API
    // However, if we store in .storage/anova_api.recipes, we might need a custom ws command.
    // To ensure full standalone functionality, another way is leveraging input_selects or requesting it 
    // from the backend. 
    // Let's implement a workaround: we can invoke an event or just let the user see their recipes.
    // For the sake of the exercise, let's pretend we have a `get_recipes` service that returns state,
    // or better yet, we can check the `select.anova_apo_...` entity's `options` to list names.
    if (!this.hass) return;
    
    // Attempt to read recipes from the `options` attribute of any anova recipe select entity!
    const states = this.hass.states;
    let names = [];
    for (const [entityId, stateObj] of Object.entries(states)) {
      if (entityId.startsWith('select.anova_') && entityId.includes('_recipe')) {
        names = stateObj.attributes.options || [];
        break;
      }
    }
    
    // Filter out "None"
    names = names.filter(n => n !== "None");
    this.recipes = names.map(n => ({ name: n, stages: [] }));
  }

  _handleSearch(e) {
    this.searchQuery = e.target.value.toLowerCase();
  }

  _startCreate() {
    this.editingRecipe = { name: "New Recipe " + Math.floor(Math.random()*100), stages: [] };
  }

  _startEdit(recipe) {
    this.editingRecipe = { ...recipe };
  }

  _addStage() {
    if (!this.editingRecipe) return;
    this.editingRecipe.stages = [...this.editingRecipe.stages, {
      id: crypto.randomUUID ? crypto.randomUUID() : "uuid-1234",
      do: {
        type: "cook",
        temperatureBulbs: { mode: "dry", dry: { setpoint: { celsius: 100 } } },
        heatingElements: { top: { on: false }, bottom: { on: true }, rear: { on: true } },
        fan: { speed: 100 },
        exhaustVent: { state: "closed" }
      }
    }];
    this.requestUpdate();
  }

  async _saveRecipe() {
    if (!this.editingRecipe) return;
    await this.hass.callService("anova_api", "save_recipe", {
      name: this.editingRecipe.name,
      stages: this.editingRecipe.stages
    });
    this.editingRecipe = null;
    // Delay slightly to let backend sync, then re-fetch
    setTimeout(() => this._fetchRecipes(), 1000);
  }

  async _deleteRecipe(name) {
    await this.hass.callService("anova_api", "delete_recipe", { name });
    setTimeout(() => this._fetchRecipes(), 1000);
  }

  render() {
    if (this.editingRecipe) {
      return this.renderEditor();
    }
    
    const filtered = this.recipes.filter(r => r.name.toLowerCase().includes(this.searchQuery));

    return html`
      <div class="container">
        <div class="header">
          <h1>Anova Recipes</h1>
          <button @click=${this._startCreate}>+ New Recipe</button>
        </div>
        
        <div class="search-bar">
          <input type="text" placeholder="Search recipes..." @input=${this._handleSearch} .value=${this.searchQuery} />
        </div>

        <ul class="recipe-list">
          ${filtered.length === 0 ? html`<p>No recipes found.</p>` : ''}
          ${filtered.map(r => html`
            <li class="recipe-item">
              <span>${r.name}</span>
              <div>
                <button @click=${() => this._startEdit(r)}>Edit</button>
                <button class="danger" @click=${() => this._deleteRecipe(r.name)}>Delete</button>
              </div>
            </li>
          `)}
        </ul>
      </div>
    `;
  }

  renderEditor() {
    return html`
      <div class="container">
        <div class="header">
          <h1>Edit Recipe</h1>
          <div>
            <button @click=${() => { this.editingRecipe = null; }}>Cancel</button>
            <button class="primary" @click=${this._saveRecipe}>Save Recipe</button>
          </div>
        </div>
        
        <label>Recipe Name
          <input type="text" .value=${this.editingRecipe.name} @input=${e => this.editingRecipe.name = e.target.value} />
        </label>
        
        <h3>Stages</h3>
        ${this.editingRecipe.stages.map((stage, i) => html`
          <div class="stage-card">
            <h4>Stage ${i + 1}</h4>
            <p>Target Temp (C): <input type="number" .value=${stage.do?.temperatureBulbs?.dry?.setpoint?.celsius || 100} 
                  @input=${e => stage.do.temperatureBulbs.dry.setpoint.celsius = parseInt(e.target.value)} /></p>
            <p>Fan Speed (%): <input type="number" .value=${stage.do?.fan?.speed || 100} 
                  @input=${e => stage.do.fan.speed = parseInt(e.target.value)} /></p>
          </div>
        `)}
        <button @click=${this._addStage}>+ Add Stage</button>
      </div>
    `;
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 24px;
        background-color: var(--primary-background-color, #fafafa);
        color: var(--primary-text-color, #212121);
        font-family: Roboto, sans-serif;
      }
      .container {
        max-width: 800px;
        margin: 0 auto;
        background: var(--card-background-color, white);
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
      }
      .search-bar {
        position: sticky;
        top: 0;
        background: inherit;
        padding: 8px 0;
        margin-bottom: 16px;
      }
      .search-bar input {
        width: 100%;
        padding: 12px;
        font-size: 16px;
        border: 1px solid #ddd;
        border-radius: 4px;
        box-sizing: border-box;
      }
      .recipe-list {
        list-style: none;
        padding: 0;
      }
      .recipe-item {
        display: flex;
        justify-content: space-between;
        padding: 16px;
        border: 1px solid #eee;
        border-radius: 4px;
        margin-bottom: 8px;
      }
      .stage-card {
        border: 1px dashed #ccc;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 4px;
      }
      button {
        padding: 8px 16px;
        background: var(--primary-color, #03a9f4);
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }
      button.danger {
        background: var(--error-color, #f44336);
      }
      input[type="text"], input[type="number"] {
        padding: 8px;
        margin-left: 8px;
        border: 1px solid #ccc;
        border-radius: 4px;
      }
    `;
  }
}
customElements.define("anova-panel", AnovaPanel);
