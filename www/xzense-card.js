/* Xzense panel card 0.5.26. No external libraries or Home Assistant plugins. */
const XZ_FIELDS = [
  {key:'device_state_localized',name:'Driftsstatus',domain:'sensor',tab:'main'},
  {key:'chimney_temperature',name:'Pipetemperatur',domain:'sensor',tab:'main'},
  {key:'fan_speed',name:'Faktisk viftehastighet',domain:'sensor',tab:'main'},
  {key:'inside_temperature',name:'Innetemperatur',domain:'sensor',tab:'main'},
  {key:'outside_temperature',name:'Utetemperatur',domain:'sensor',tab:'main'},
  {key:'pressure',name:'Lufttrykk',domain:'sensor',tab:'main'},
  {key:'fire_duration',name:'Fyringsvarighet',domain:'sensor',tab:'main'},
  {key:'battery',name:'Batteri kontrollpanel',domain:'sensor',tab:'main'},
  {key:'signal_strength',name:'Radiolink – signalstyrke (0–3)',domain:'sensor',tab:'main'},
  {key:'start_fire',name:'Start fyring',domain:'button',tab:'main'},
  {key:'refuel',name:'Legg på ved',domain:'button',tab:'main'},
  {key:'stop_fire',name:'Avslutt fyring',domain:'button',tab:'main'},
  {key:'boost',name:'Boost',domain:'switch',tab:'main'},
  {key:'ventilation',name:'Ventilasjon',domain:'switch',tab:'main'},
  {key:'user_fan_speed',name:'Viftehastighet',domain:'number',tab:'operating'},
  {key:'boost_fan_speed',name:'Boost-hastighet',domain:'number',tab:'operating'},
  {key:'auto_start_temperature',name:'Starttemperatur',domain:'number',tab:'operating'},
  {key:'auto_stop_temperature',name:'Stopptemperatur',domain:'number',tab:'operating'},
  {key:'boost_time',name:'Boost-tid',domain:'number',tab:'operating'},
  {key:'afterrun_time',name:'Ettergangstid',domain:'number',tab:'operating'},
  {key:'refire_time',name:'Gjenfyrings-tid',domain:'number',tab:'operating'},
  {key:'burnout_time',name:'Utbrenningstid',domain:'number',tab:'operating'},
  {key:'alarm_setpoint',name:'Alarmtemperatur',domain:'number',tab:'operating'},
  {key:'boost_stop_temperature',name:'Boost-stopptemperatur',domain:'number',tab:'operating'},
  {key:'wanted_draft',name:'Pipetrekk',domain:'number',tab:'configuration'},
  {key:'minimum_fan_voltage',name:'Minimum viftespenning',domain:'number',tab:'operating'},
  {key:'system_control',name:'Systemstyring',domain:'select',tab:'configuration'},
  {key:'temperature_sensor',name:'Temperaturføler',domain:'switch',tab:'configuration'},
  {key:'rs009_41_motor',name:'Viftetype RS009-41',domain:'switch',tab:'configuration'},
  {key:'brightness_raw',name:'Lysstyrke',domain:'number',tab:'display'},
  {key:'contrast_raw',name:'Kontrast',domain:'number',tab:'display'},
  {key:'volume_raw',name:'Lydstyrke',domain:'number',tab:'display'},
  {key:'bluetooth_update_interval',name:'Bluetooth i hvile (Ready)',domain:'number',tab:'configuration'},
  {key:'bluetooth_active_update_interval',name:'Bluetooth under aktiv drift',domain:'number',tab:'configuration'},
  {key:'ble_link_connected',name:'Bluetooth-link',domain:'sensor',tab:'diagnostics'},
  {key:'phase',name:'Tilkoblingsfase',domain:'sensor',tab:'diagnostics'},
  {key:'last_advertisement_rssi',name:'RSSI',domain:'sensor',tab:'diagnostics'},
  {key:'selected_source',name:'Valgt Bluetooth-kilde',domain:'sensor',tab:'diagnostics'},
  {key:'last_error',name:'Siste Bluetooth-feil',domain:'sensor',tab:'diagnostics'},
  {key:'last_data_at',name:'Sist oppdatert (Bluetooth)',domain:'sensor',tab:'diagnostics'},
  {key:'last_successful_bt_status',name:'Sist vellykket Bluetooth-oppdatering',domain:'sensor',tab:'diagnostics'},
  {key:'next_poll_at',name:'Neste Bluetooth-oppdatering',domain:'sensor',tab:'diagnostics'},
];
// Display-only translation of the legacy English state sensor. Raw entity state
// is left untouched so existing automations keep working.
const XZ_STATE_KEYS = {"Offline":"offline","Setup":"setup","Ready for lighting":"ready_for_lighting","Boosting":"boosting","Operation":"operation","Burnout":"burnout","Afterrun":"afterrun","Refueling":"refueling","Ventilation":"ventilation","Error":"error","Upgrading":"upgrading"};
const XZ_STATE_NB = {"offline":"Frakoblet","setup":"Oppsett","ready_for_lighting":"Klar for fyring","boosting":"Boost","operation":"Drift","burnout":"Utbrenning","afterrun":"Ettergang","refueling":"Påfylling av ved","ventilation":"Ventilasjon","error":"Feil","upgrading":"Oppdatering","unknown_state":"Ukjent tilstand"};
const XZ_TABS = [
  ['main','Hovedskjerm','mdi:fireplace'],
  ['operating','Driftsinnstillinger','mdi:tune-vertical'],
  ['configuration','Konfigurasjon','mdi:cog-outline'],
  ['display','Kontrollpanel','mdi:monitor'],
  ['diagnostics','Diagnostikk','mdi:bluetooth'],
];
const XZ_GLOBAL_IDS = {
  user_fan_speed:'0x50',boost_fan_speed:'0x4F',auto_start_temperature:'0x4B',
  auto_stop_temperature:'0x4C',boost_time:'0x4D',afterrun_time:'0x4E',
  boost_stop_temperature:'0x52',wanted_draft:'0x53',minimum_fan_voltage:'0x54',
  system_control:'0x55',temperature_sensor:'0x56',alarm_setpoint:'0x58',
  refire_time:'0x59',burnout_time:'0x5B',brightness_raw:'0x34',
  contrast_raw:'0x33',volume_raw:'0x32',
};
const XZ_STYLES = `
  :host {display:block;--xz-accent:var(--primary-color,#448aff);--xz-muted:var(--secondary-text-color,#6a7080)}
  * {box-sizing:border-box} .root{color:var(--primary-text-color,#202124);background:var(--card-background-color,#fff);border-radius:var(--ha-card-border-radius,14px);border:1px solid var(--divider-color,#ddd);overflow:hidden}
  .head{padding:15px 17px 10px;display:flex;align-items:center;justify-content:space-between;gap:12px}
  .head-title{font-size:1.12rem;font-weight:650}.sub{font-size:.79rem;color:var(--xz-muted);margin-top:3px}
  .head-battery{display:flex;align-items:center;gap:4px;flex:none;font-size:.86rem;font-weight:600;font-variant-numeric:tabular-nums;color:var(--primary-text-color,#202124)}.head-battery ha-icon{--mdc-icon-size:23px}
  .tabs{display:flex;gap:2px;overflow:auto;padding:0 10px 9px;border-bottom:1px solid var(--divider-color,#ddd)}
  .tab{font:inherit;color:var(--xz-muted);white-space:nowrap;font-size:.82rem;background:transparent;border:0;border-radius:9px;padding:10px;cursor:pointer}
  .tab[aria-selected=true]{color:var(--xz-accent);background:color-mix(in srgb,var(--xz-accent) 10%,transparent);font-weight:650}
  .panel{padding:16px;display:grid;gap:14px}.hero{background:var(--secondary-background-color,#f5f6f7);padding:18px;border-radius:12px}
  .big{font-size:2.25rem;font-weight:700;line-height:1.25}.hero-label{font-size:.86rem;color:var(--xz-muted)}
  .freshness{display:flex;align-items:center;gap:10px;margin-top:10px;color:var(--xz-muted);font-size:.79rem;line-height:1.45}
  .bt-freshness{display:flex;align-items:center;gap:7px;flex:1;min-width:0;flex-wrap:wrap}.freshness strong{color:var(--primary-text-color,#202124);font-weight:600}.bt-freshness ha-icon{--mdc-icon-size:16px}
  .radiolink{display:flex;align-items:center;gap:5px;flex:none;margin-left:auto;color:var(--primary-text-color,#202124)}.radiolink ha-icon{--mdc-icon-size:22px}
  .signal-bars{height:19px;display:flex;align-items:flex-end;gap:3px}.signal-bar{display:block;width:4px;border-radius:2px 2px 0 0;background:var(--divider-color,#c2c6cd)}.signal-bar:nth-child(1){height:7px}.signal-bar:nth-child(2){height:12px}.signal-bar:nth-child(3){height:17px}.signal-bar.active{background:var(--primary-text-color,#202124)}
  .stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}
  .stat{border-radius:8px;padding:9px;background:var(--card-background-color,#fff);min-width:0}
  .stat small{display:block;color:var(--xz-muted);font-size:.73rem}.stat strong{display:block;overflow-wrap:anywhere;font-size:.95rem;margin-top:4px}
  .group{display:grid;gap:10px}.group h4{margin:0 0 2px;font-size:.91rem}.controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
  .action{font:inherit;border:1px solid var(--divider-color,#ccc);border-radius:9px;padding:11px 8px;background:var(--secondary-background-color,#fafafa);color:var(--primary-text-color,#222);cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px}
  .action.on{color:var(--xz-accent);border-color:var(--xz-accent)}.action:disabled,.set:disabled{opacity:.48;cursor:not-allowed}
  .rowset{padding:12px;border:1px solid var(--divider-color,#ddd);border-radius:10px;display:grid;gap:9px}
  .rowhead{display:flex;align-items:center;justify-content:space-between;gap:8px}.val{font-size:.91rem;color:var(--xz-muted);font-variant-numeric:tabular-nums}
  .setter{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.setter input[type=range]{flex:1;min-width:100px;accent-color:var(--xz-accent)}
  .setter input[type=number]{width:112px;min-width:90px;padding:10px;font:inherit;border:1px solid var(--divider-color,#ddd);color:inherit;background:var(--card-background-color,#fff);border-radius:8px}
  .setter select{flex:1;min-width:100px;padding:10px;font:inherit;color:inherit;border:1px solid var(--divider-color,#ddd);border-radius:8px;background:var(--card-background-color,#fff)}
  .set{font:inherit;color:var(--primary-text-color,#222);background:var(--secondary-background-color,#f4f4f4);border:1px solid var(--divider-color,#ddd);border-radius:8px;padding:10px 13px;cursor:pointer}
  .warn{font-size:.78rem;color:var(--error-color,#b71c1c);line-height:1.45}.note{font-size:.82rem;color:var(--xz-muted);line-height:1.45}
  .missing{color:var(--error-color,#b71c1c);font-size:.77rem}.diag{display:grid;gap:0}.diagline{display:grid;grid-template-columns:40% 60%;padding:9px 0;border-bottom:1px solid var(--divider-color,#ddd);gap:10px;overflow-wrap:anywhere;font-size:.84rem}
  .diagline span{color:var(--xz-muted)}.status{font-size:.82rem;color:var(--xz-muted)}.tip{border:1px dashed var(--divider-color,#bbb);padding:11px;border-radius:9px;font-size:.8rem;line-height:1.5}
  .footer{border-top:1px solid var(--divider-color,#ddd);color:var(--xz-muted);padding:8px 16px;font-size:.71rem}
  @media(max-width:420px){.tabs .tlabel{display:none}.tab{flex:1}.stats{grid-template-columns:repeat(2,minmax(0,1fr))}.controls{grid-template-columns:repeat(2,minmax(0,1fr))}}
`;
function xzEsc(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function xzSlug(value){return String(value??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]/g,'');}
class XzenseCard extends HTMLElement {
  constructor(){super();this.attachShadow({mode:'open'});this._config={};this._hass=null;this._tab='main';this._lastProblem='';}
  setConfig(config){this._config={title:'Xzense',...config,entities:{...(config.entities||{})},labels:{...(config.labels||{})}};this._render();}
  set hass(hass){this._hass=hass;if(this.shadowRoot.activeElement?.matches('input,select'))return;this._render();}
  static getConfigElement(){return document.createElement('xzense-card-editor');}
  static getStubConfig(){return {type:'custom:xzense-card',title:'Xzense',entities:{}};}
  getCardSize(){return 6;}
  _field(key){return XZ_FIELDS.find(f=>f.key===key);}
  _label(key){return this._config.labels?.[key] || this._field(key)?.name || key;}
  _entity(key){
    const manually=this._config.entities?.[key];
    if(manually)return manually;
    if(!this._hass)return null;
    const field=this._field(key);if(!field)return null;
    const names=Object.keys(this._hass.states||{}).filter(e=>e.startsWith(field.domain+'.'));
    // Autolink only on an *unambiguous* match. No cross-device guessing.
    let candidates=names.filter(id => this._hass.states[id]?.attributes?.global_id === XZ_GLOBAL_IDS[key]);
    if(candidates.length===1)return candidates[0];
    const exact=names.filter(id=>{
      const state=this._hass.states[id];
      const raw=id.split('.')[1];
      const friendly=String(state?.attributes?.friendly_name||'').toLowerCase();
      const xzenseNamed = raw.includes('xzense') || friendly.includes('xzense');
      const oldUpdateName = key==='last_data_at' && xzenseNamed && (raw.endsWith('_last_data_update') || raw.endsWith('_sist_oppdatert_bluetooth'));
      return raw===key || raw.endsWith('_'+key) || oldUpdateName || (friendly.includes('xzense') && xzSlug(friendly).endsWith(xzSlug(this._field(key).name)));
    });
    return exact.length===1?exact[0]:null;
  }
  _state(key){const id=this._entity(key);return id?this._hass?.states?.[id]:null;}
  _translatedDeviceState(raw){
    const key=XZ_STATE_KEYS[String(raw)] || (Object.hasOwn(XZ_STATE_NB,String(raw))?String(raw):null);
    if(!key){const unknown=String(raw).match(/^Unknown \((\d+)\)$/);return unknown?`Ukjent tilstand (${unknown[1]})`:raw;}
    const translationId=`component.xzense_full_preview.entity.sensor.device_state_localized.state.${key}`;
    const localized=typeof this._hass?.localize==='function'?this._hass.localize(translationId):null;
    return localized && localized!==translationId ? localized : (XZ_STATE_NB[key] || raw);
  }
  _format(key){
    const s=this._state(key);
    if(!s||!s.state||['unavailable','unknown'].includes(s.state))return '–';
    if(key==='device_state_localized')return this._translatedDeviceState(s.state);
    if(['bluetooth_update_interval','bluetooth_active_update_interval'].includes(key)&&Number(s.state)===0)return 'Kontinuerlig';
    return s.state+(s.attributes?.unit_of_measurement?' '+s.attributes.unit_of_measurement:'');
  }
  _lastUpdatedInfo(){
    const rawSensor=this._state('last_successful_bt_status')?.attributes?.timestamp_iso||this._state('last_data_at')?.state;
    const valid=value=>value && !['unavailable','unknown','none'].includes(String(value).toLowerCase());
    const raw=valid(rawSensor)?rawSensor:
      ['chimney_temperature','device_state','inside_temperature','outside_temperature','pressure']
        .map(key=>this._state(key)?.attributes?.last_data_at).find(valid);
    if(!raw || ['unavailable','unknown','none'].includes(String(raw).toLowerCase()))return {time:'–',age:'Ingen mottatte data ennå'};
    const stamp=new Date(raw), timestamp=stamp.getTime();
    if(!Number.isFinite(timestamp))return {time:'–',age:'Ukjent tidspunkt'};
    const seconds=Math.max(0,Math.floor((Date.now()-timestamp)/1000));
    const age=seconds<60?'nettopp':seconds<3600?`for ${Math.floor(seconds/60)} min siden`:seconds<86400?`for ${Math.floor(seconds/3600)} t siden`:`for ${Math.floor(seconds/86400)} d siden`;
    const local=this._state('last_successful_bt_status')?.state;
    const time=valid(local)?local:stamp.toLocaleString('nb-NO',{timeZone:this._hass?.config?.time_zone||'Europe/Oslo',day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}).replace(', ',' kl. ');
    return {time,age};
  }
  _lastUpdatedLine(){const info=this._lastUpdatedInfo();return `${info.time} (${info.age})`;}
  _ready(key){const e=this._state(key);return !!e && !['unavailable','unknown'].includes(e.state);}
  _tabButton(t){return `<button class="tab" data-tab="${t[0]}" aria-selected="${this._tab===t[0]}"><ha-icon icon="${t[2]}"></ha-icon> <span class="tlabel">${t[1]}</span></button>`;}
  _stat(key){return `<div class="stat"><small>${xzEsc(this._label(key))}</small><strong>${xzEsc(this._format(key))}</strong></div>`;}
  _batteryIndicator(){const raw=this._state('battery')?.state;const percent=Number(raw);const valid=raw!==undefined&&raw!==null&&String(raw).trim()!==''&&Number.isFinite(percent)&&percent>=0&&percent<=100;const level=valid?Math.round(percent):0;const icon=!valid?'mdi:battery-unknown':level===100?'mdi:battery':level===0?'mdi:battery-outline':`mdi:battery-${Math.min(90,Math.max(10,Math.ceil(level/10)*10))}`;const label=valid?`Batteri kontrollpanel: ${level} %`:'Batteri kontrollpanel: ukjent';return `<div class="head-battery" title="${xzEsc(label)}" aria-label="${xzEsc(label)}"><ha-icon icon="${icon}"></ha-icon><span>${valid?`${level} %`:'–'}</span></div>`;}
  _radioLink(){const raw=this._state('signal_strength')?.state;const number=Number(raw);const valid=raw!==undefined&&raw!==null&&String(raw).trim()!==''&&Number.isInteger(number)&&number>=0&&number<=3;const level=valid?number:0;const label=valid?`Radiolink signalstyrke ${level} av 3`:'Radiolink signalstyrke ukjent';const bars=[1,2,3].map(i=>`<span class="signal-bar${valid&&level>=i?' active':''}"></span>`).join('');return `<div class="radiolink" role="img" aria-label="${xzEsc(label)}" title="${xzEsc(label)}"><ha-icon icon="mdi:z-wave"></ha-icon><span class="signal-bars" aria-hidden="true">${bars}</span></div>`;}
  _action(key,icon){const e=this._state(key);const linked=!!this._entity(key);const ready=this._ready(key);const on=e?.state==='on';const afterrun=key==='start_fire' && /afterrun|ettergang/i.test(this._state('device_state_localized')?.state||'');const label=afterrun&&!this._config.labels?.start_fire?'Start ny fyring':this._label(key);return `<button class="action ${on?'on':''}" data-action="${key}" ${ready?'':'disabled'} title="${xzEsc(linked?'':'Velg riktig entitet i kortredigeringen')}"><ha-icon icon="${icon}"></ha-icon>${xzEsc(label)}${!linked?' ⚠':''}</button>`;}
  _numeric(key,slider=false){const e=this._state(key), a=e?.attributes||{}, v=e?.state, ready=this._ready(key), num=ready?Number(v):NaN;
    const low=Number.isFinite(Number(a.min))?Number(a.min):(slider?0:0),high=Number.isFinite(Number(a.max))?Number(a.max):(slider?100:100),step=Number(a.step)>0?Number(a.step):1;
    const shown=Number.isFinite(num)?String(num):'';
    const inp=slider?`<input type="range" data-number="${key}" min="${low}" max="${high}" step="${step}" value="${shown||low}" ${ready?'':'disabled'}>`:
    `<input type="number" data-number="${key}" min="${low}" max="${high}" step="${step}" value="${shown}" ${ready?'':'disabled'} aria-label="${xzEsc(this._label(key))}">`;
    const factory=a.factory_reference!==null&&a.factory_reference!==undefined?`<div class="note">Standardreferanse: ${xzEsc(a.factory_reference)}${xzEsc(a.unit_of_measurement||'')}</div>`:'';
    const voltageWarning=key==='minimum_fan_voltage'&&a.under_motor_minimum?'<div class="warn">RS009-41 er aktivert, men kontrollpanelet står under 100 V. Velg en verdi fra 100 til 120 V og lagre.</div>':'';
    return `<div class="rowset"><div class="rowhead"><strong>${xzEsc(this._label(key))}</strong><span class="val">${xzEsc(this._format(key))}</span></div><div class="setter">${inp}<button class="set" data-number-save="${key}" ${ready?'':'disabled'}>Lagre</button></div>${factory}${voltageWarning}${!this._entity(key)?'<span class="missing">Entitet må velges i kortredigeringen</span>':''}</div>`;
  }
  _mode(key){const e=this._state(key),ready=this._ready(key),options=e?.attributes?.options||[];return `<div class="rowset"><div class="rowhead"><strong>${xzEsc(this._label(key))}</strong><span class="val">${xzEsc(this._format(key))}</span></div><div class="setter"><select data-select="${key}" ${ready?'':'disabled'}>${options.map(o=>`<option value="${xzEsc(o)}" ${e?.state===o?'selected':''}>${xzEsc(o)}</option>`).join('')}</select><button data-select-save="${key}" class="set" ${ready?'':'disabled'}>Lagre</button></div></div>`;}
  _toggle(key,experimental=false){const e=this._state(key);const ready=this._ready(key);return `<div class="rowset"><div class="rowhead"><strong>${xzEsc(this._label(key))}</strong><span class="val">${xzEsc(this._format(key))}</span></div><div class="setter"><button data-toggle="${key}" class="action ${e?.state==='on'?'on':''}" ${ready?'':'disabled'}><ha-icon icon="mdi:toggle-switch${e?.state==='on'?'':'-off'}"></ha-icon>${e?.state==='on'?'Slå av':'Slå på'}</button></div>${experimental?'<span class="warn">Eksperimentell GLOBAL 0x56-kontroll. Slått av = ingen automatisk temperaturbasert start/stopp. Kontroller panelet etter endring.</span>':''}</div>`;}
  _main(){const last=this._lastUpdatedInfo();return `<div class="hero"><div class="hero-label">Driftsstatus</div><div class="big">${xzEsc(this._format('device_state_localized'))}</div><div class="freshness"><div class="bt-freshness"><ha-icon icon="mdi:bluetooth"></ha-icon><span>Sist oppdatert: <strong>${xzEsc(last.time)}</strong> · ${xzEsc(last.age)}</span></div>${this._radioLink()}</div><div class="stats">${['chimney_temperature','fan_speed','fire_duration','inside_temperature','outside_temperature','pressure'].map(k=>this._stat(k)).join('')}</div></div><div class="group"><h4>Fyring og ventilasjon</h4><div class="controls">${this._action('start_fire','mdi:fire')}${this._action('refuel','mdi:forest')}${this._action('stop_fire','mdi:fire-off')}${this._action('boost','mdi:turbine')}${this._action('ventilation','mdi:fan')}</div></div><div class="group"><h4>Vifte</h4>${this._numeric('user_fan_speed',true)}</div>`;}
  _operating(){return `<div class="group"><h4>Hastigheter</h4>${this._numeric('user_fan_speed',true)}${this._numeric('boost_fan_speed',true)}</div><div class="group"><h4>Temperaturer</h4>${['auto_start_temperature','auto_stop_temperature','boost_stop_temperature','alarm_setpoint'].map(k=>this._numeric(k)).join('')}</div><div class="group"><h4>Tider</h4>${['boost_time','afterrun_time','refire_time','burnout_time'].map(k=>this._numeric(k)).join('')}</div><div class="group"><h4>Viftegrense</h4>${this._numeric('minimum_fan_voltage')}</div>`;}
  _configuration(){return `<div class="group"><h4>Bluetooth</h4><div class="note">0 = kontinuerlig Bluetooth. Hvile (Ready): 0–120 min, standard 5. Aktiv (Boosting, Operation, Afterrun og Ventilation): 0–600 sekunder, standard 0. Knappetrykk kobler til ved behov. Verdier beholdes ved frakobling.</div>${this._numeric('bluetooth_update_interval',true)}${this._numeric('bluetooth_active_update_interval',true)}</div><div class="group"><h4>Viftetype</h4><div class="note">RS009-41 på: minste viftespenning begrenses lokalt til 100–120 V. Av: 80–120 V. Valget endrer ikke spenningen på kontrollpanelet automatisk.</div>${this._toggle('rs009_41_motor')}</div><div class="group"><h4>Pipetrekk (installasjon)</h4><div class="note">Dette er lagret installasjonsverdi og ikke målt pipetrekk. Ingen XTP-trykksensor er montert.</div>${this._numeric('wanted_draft')}</div>${this._mode('system_control')}${this._toggle('temperature_sensor')}<div class="note">Trykkstyring (XTP), språk og firmwareoppdatering er bevisst ikke eksponert.</div>`;}
  _display(){return `<div class="note">Displayinnstillinger fra Xzense-panelet, 0–100 %. Verdiene skrives først når du trykker Lagre.</div>${['brightness_raw','contrast_raw','volume_raw'].map(k=>this._numeric(k,true)).join('')}`;}
  _diagnostics(){return `<div class="diag">${['ble_link_connected','phase','last_successful_bt_status','next_poll_at','last_advertisement_rssi','selected_source','last_error'].map(k=>`<div class="diagline"><span>${xzEsc(this._label(k))}</span><strong>${xzEsc(this._format(k))}</strong></div>`).join('')}</div><div class="note">Fullstendig protokolldiagnostikk er tilgjengelig i Home Assistants integrasjonsdiagnostikk.</div>`;}
  _render(){if(!this._config)return;const contents={main:()=>this._main(),operating:()=>this._operating(),configuration:()=>this._configuration(),display:()=>this._display(),diagnostics:()=>this._diagnostics()};
    const missing=XZ_FIELDS.filter(f=>f.tab===this._tab&&!this._entity(f.key)).length;
    this.shadowRoot.innerHTML=`<style>${XZ_STYLES}</style><ha-card class="root"><div class="head"><div><div class="head-title">${xzEsc(this._config.title||'Xzense')}</div><div class="sub">${this._hass?'Panelstyring via Home Assistant':'Laster Home Assistant…'}</div></div>${this._batteryIndicator()}</div><div class="tabs">${XZ_TABS.map(t=>this._tabButton(t)).join('')}</div><div class="panel">${contents[this._tab]()}${missing?`<div class="tip">${missing} felt mangler entitetskobling i denne fanen. Velg <strong>Rediger dashboard → Rediger kort</strong> for å koble riktig entitet til hver funksjon.</div>`:''}${this._lastProblem?`<div class="warn">${xzEsc(this._lastProblem)}</div>`:''}</div><div class="footer">Xzense-kort 0.5.26 · bruker faktiske Home Assistant-entiteter</div></ha-card>`;
    this.shadowRoot.querySelectorAll('[data-tab]').forEach(n=>n.addEventListener('click',()=>{this._tab=n.dataset.tab;this._lastProblem='';this._render()}));
    this.shadowRoot.querySelectorAll('[data-action]').forEach(n=>n.addEventListener('click',()=>this._doAction(n.dataset.action)));
    this.shadowRoot.querySelectorAll('[data-toggle]').forEach(n=>n.addEventListener('click',()=>this._doAction(n.dataset.toggle)));
    this.shadowRoot.querySelectorAll('[data-number-save]').forEach(n=>n.addEventListener('click',()=>this._numberSave(n.dataset.numberSave)));
    this.shadowRoot.querySelectorAll('[data-select-save]').forEach(n=>n.addEventListener('click',()=>this._selectSave(n.dataset.selectSave)));
  }
  async _send(domain, service, key, extra={}){const id=this._entity(key);if(!id){this._lastProblem=`Ingen entitet knyttet til ${this._label(key)}.`;this._render();return;}
    if(!this._ready(key)){this._lastProblem=`${this._label(key)} er utilgjengelig.`;this._render();return;}
    try{await this._hass.callService(domain,service,{entity_id:id,...extra});this._lastProblem='';}
    catch(err){this._lastProblem=`Kunne ikke styre ${this._label(key)}: ${err?.message||err}`;}
    this._render();}
  _doAction(key){const f=this._field(key);if(!f)return;
    if(f.domain==='button')return this._send('button','press',key);
    if(f.domain==='switch'){
      const on=this._state(key)?.state==='on';
      if(key==='temperature_sensor'&&on&&!confirm('Deaktivere temperaturprobe? Dette deaktiverer også automatisk temperaturbasert start og stopp. Kontrollér endringen på Xzense-panelet.'))return;
      return this._send('switch',on?'turn_off':'turn_on',key);
    }
  }
  _numberSave(key){const input=this.shadowRoot.querySelector(`[data-number="${key}"]`);const value=Number(input?.value);
    if(!input||!Number.isFinite(value))return;const min=Number(input.min),max=Number(input.max);
    if(value<min||value>max){this._lastProblem=`${this._label(key)} må være mellom ${min} og ${max}.`;this._render();return;}
    return this._send('number','set_value',key,{value});
  }
  _selectSave(key){const select=this.shadowRoot.querySelector(`[data-select="${key}"]`);if(select)return this._send('select','select_option',key,{option:select.value});}
}
class XzenseCardEditor extends HTMLElement{
  constructor(){super();this.attachShadow({mode:'open'});this._config={type:'custom:xzense-card',title:'Xzense',entities:{},labels:{}};this._hass=null;}
  setConfig(config){this._config={...config,entities:{...(config.entities||{})},labels:{...(config.labels||{})}};this._render();}
  set hass(hass){this._hass=hass;if(this.shadowRoot.activeElement?.matches('input,select'))return;this._render();}
  _changed(){this.dispatchEvent(new CustomEvent('config-changed',{detail:{config:{...this._config}},bubbles:true,composed:true}));}
  _render(){const ent=this._config.entities||{};const labels=this._config.labels||{};
    const groups=[['Hovedskjerm','main'],['Driftsinnstillinger','operating'],['Konfigurasjon','configuration'],['Kontrollpanel','display'],['Diagnostikk','diagnostics']];
    const rows=groups.map(([name,tab])=>`<section><h3>${name}</h3>${XZ_FIELDS.filter(f=>f.tab===tab).map(f=>{
      const options=Object.keys(this._hass?.states||{}).filter(e=>e.startsWith(f.domain+'.'));
      const selected=ent[f.key]||'';
      const displayList=options.sort((a,b)=>{const aa=a.includes('xzense')?0:1,bb=b.includes('xzense')?0:1;return aa-bb||a.localeCompare(b)});
      return `<div class="field"><label for="map_${f.key}">${xzEsc(f.name)}</label><select id="map_${f.key}" data-entity="${f.key}"><option value="">Automatisk (kun sikker match)</option>${selected&&!displayList.includes(selected)?`<option selected value="${xzEsc(selected)}">${xzEsc(selected)} (ikke tilgjengelig)</option>`:''}${displayList.map(id=>`<option value="${xzEsc(id)}" ${selected===id?'selected':''}>${xzEsc(id)} · ${xzEsc(this._hass.states[id]?.attributes?.friendly_name||'')}</option>`).join('')}</select><input data-label="${f.key}" aria-label="Visningsnavn ${xzEsc(f.name)}" placeholder="Visningsnavn (valgfritt)" value="${xzEsc(labels[f.key]||'')}"></div>`;
    }).join('')}</section>`).join('');
    this.shadowRoot.innerHTML=`<style>*{box-sizing:border-box} .wrap{display:grid;gap:13px;color:var(--primary-text-color)}label{font-size:.81rem;display:block;margin-bottom:5px;font-weight:600}input,select{display:block;width:100%;font:inherit;font-size:.87rem;border:1px solid var(--divider-color,#bbb);border-radius:7px;padding:8px;background:var(--card-background-color,#fff);color:var(--primary-text-color,#222)}section{border-top:1px solid var(--divider-color,#ccc);padding-top:8px}section h3{font-size:.96rem}.field{margin-bottom:13px;display:grid;gap:6px}.info{font-size:.8rem;line-height:1.5;color:var(--secondary-text-color,#666)}</style><div class="wrap"><label>Tittel<input id="title" value="${xzEsc(this._config.title||'Xzense')}"></label><div class="info">Velg riktig Home Assistant-entitet for hver Xzense-funksjon. Endringene lagres sammen med dashboardet og gjelder på alle enheter. Valgfritt visningsnavn endrer bare teksten på kortet, ikke Home Assistant-entiteten.</div>${rows}</div>`;
    this.shadowRoot.getElementById('title').addEventListener('change',e=>{this._config.title=e.target.value;this._changed()});
    this.shadowRoot.querySelectorAll('[data-entity]').forEach(el=>el.addEventListener('change',e=>{const key=e.target.dataset.entity;this._config.entities={...(this._config.entities||{})};if(e.target.value)this._config.entities[key]=e.target.value;else delete this._config.entities[key];this._changed()}));
    this.shadowRoot.querySelectorAll('[data-label]').forEach(el=>el.addEventListener('change',e=>{const key=e.target.dataset.label;this._config.labels={...(this._config.labels||{})};if(e.target.value.trim())this._config.labels[key]=e.target.value.trim();else delete this._config.labels[key];this._changed()}));
  }
}
if(!customElements.get('xzense-card'))customElements.define('xzense-card',XzenseCard);
if(!customElements.get('xzense-card-editor'))customElements.define('xzense-card-editor',XzenseCardEditor);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==='xzense-card'))window.customCards.push({type:'xzense-card',name:'Xzense Kontrollpanel',description:'Xzense med norsk meny og valgfrie Home Assistant-entiteter',preview:true});
console.info('%c Xzense Dashboard 0.5.26','color:#1976d2;font-weight:bold');
