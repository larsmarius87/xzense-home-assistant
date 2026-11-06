// Integration-style regression tests for Xzense card entity/device discovery.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const components = new Map();
const win = {customCards: []};
class HTMLElementMock {
  attachShadow() {
    this.shadowRoot = {
      activeElement: null,
      innerHTML: '',
      querySelectorAll: () => [],
      getElementById: () => ({addEventListener: () => {}}),
    };
    return this.shadowRoot;
  }
}
const ctx = {
  HTMLElement: HTMLElementMock,
  customElements: {
    get: name => components.get(name),
    define: (name, cls) => components.set(name, cls),
  },
  window: win,
  console,
  Date,
  setTimeout,
};
vm.runInNewContext(fs.readFileSync('tools/xzense_card_05281.js', 'utf8'), ctx, {
  filename: 'xzense_card_05281.js',
});

const Card = components.get('xzense-card');
assert(Card, 'Custom card registered');

function hassWith(devices, entities) {
  const calls = [];
  const connection = {
    sendMessagePromise: async req => {
      calls.push(req.type);
      if (req.type === 'config/entity_registry/list') return entities;
      if (req.type === 'config/device_registry/list') return devices;
      throw Error('Unexpected registry request');
    },
  };
  const states = {};
  for (const entry of entities) {
    states[entry.entity_id] = {
      state: '1',
      attributes: {friendly_name: 'Custom display name'},
    };
  }
  return {connection, states, config: {time_zone: 'Europe/Oslo'}, calls};
}

const device = (id, mac) => ({
  id, name: 'Xzense ' + id, identifiers: [['xzense', mac]],
});
const entity = (id, device_id, unique_id) => ({
  entity_id: id, device_id, unique_id, platform: 'xzense',
});
async function settle() {
  // Waiting for the two registry queries and the subsequent card render.
  for (let i=0;i<6;i++) await Promise.resolve();
}
(async () => {
  const mac='84:8B:CD:50:36:29';
  const one=hassWith(
    [device('one', mac)],
    [
      entity('sensor.my_renamed_temp','one',mac+'_chimney_temperature'),
      entity('button.another_name','one',mac+'_start_fire'),
      entity('switch.renamed_boost','one',mac+'_boost'),
      entity('number.some_value','one',mac+'_user_fan_speed'),
      // Never link unrelated platforms, even with the same identifier suffix.
      {...entity('sensor.wrong_platform','one',mac+'_pressure'),platform:'other'},
    ]
  );
  const card=new Card();
  card.setConfig({type:'custom:xzense-card'});
  card.hass=one;
  await settle();
  assert.equal(card._entity('chimney_temperature'),'sensor.my_renamed_temp');
  assert.equal(card._entity('start_fire'),'button.another_name');
  assert.equal(card._entity('boost'),'switch.renamed_boost');
  assert.equal(card._entity('user_fan_speed'),'number.some_value');
  assert.equal(card._entity('pressure'),null);
  // ButtonEntity can legitimately report unknown before the first press.
  one.states['button.another_name'].state='unknown';
  assert.equal(card._ready('start_fire'),true,'Unknown button is pressable');
  one.states['button.another_name'].state='unavailable';
  assert.equal(card._ready('start_fire'),false,'Unavailable button is blocked');
  one.states['button.another_name'].state='unknown';
  one.states['sensor.my_renamed_temp'].state='unknown';
  assert.equal(card._ready('chimney_temperature'),false,'Unknown numeric sensor is not ready');
  one.states['sensor.my_renamed_temp'].state='1';
  delete one.states['button.another_name'];
  assert.equal(card._ready('start_fire'),false,'Missing button is blocked');
  one.states['button.another_name']={state:'unknown',attributes:{}};

  assert.deepEqual(one.calls,['config/entity_registry/list','config/device_registry/list']);
  // A new card should share the same registry lookup for the same connection.
  const another=new Card();
  another.setConfig({type:'custom:xzense-card'});
  another.hass=one;
  await settle();
  assert.equal(another._entity('start_fire'),'button.another_name');
  assert.equal(one.calls.length,2);

  const mac2='AA:BB:CC:DD:EE:FF';
  const two=hassWith(
    [device('one',mac),device('two',mac2)],
    [
      entity('sensor.first','one',mac+'_chimney_temperature'),
      entity('sensor.second','two',mac2+'_chimney_temperature'),
    ]
  );
  const multiple=new Card();
  multiple.setConfig({type:'custom:xzense-card'});
  multiple.hass=two;
  await settle();
  assert.equal(multiple._entity('chimney_temperature'),null,'Two devices require selection');
  multiple.setConfig({type:'custom:xzense-card',device:'two'});
  assert.equal(multiple._entity('chimney_temperature'),'sensor.second');
  multiple.setConfig({type:'custom:xzense-card',device:'one'});
  assert.equal(multiple._entity('chimney_temperature'),'sensor.first');
  multiple.setConfig({type:'custom:xzense-card',device:'invalid'});
  assert.equal(multiple._entity('chimney_temperature'),null,'Unknown device must not be guessed');
  multiple.setConfig({type:'custom:xzense-card',device:'invalid',
    entities:{chimney_temperature:'sensor.manual_override'}});
  assert.equal(multiple._entity('chimney_temperature'),'sensor.manual_override');
  console.log('Xzense 0.5.28.3 entity discovery and button-state tests passed');
})().catch(e => {console.error(e);process.exitCode=1;});
