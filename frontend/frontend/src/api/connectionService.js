import { httpClient, httpClientWiki } from './httpClient';

const playersEndpoint = '/players';
const wikiEndpoint = '/w/api.php';

export const getAllPlayers = async (page, perPage) => {
  const res = await httpClient.get(playersEndpoint, {
    params: {page: page, per_page: perPage}
  });
  return res.data;
};

export const getPlayerById = async (id) => {
  const res = await httpClient.get(`${playersEndpoint}/${id}`);
  return res.data;
};

export const createPlayer = async (player) => {
  const res = await httpClient.post(playersEndpoint, player);
  return res.data;
};

export const updatePlayer = async (id, player) => {
  const res = await httpClient.put(`${playersEndpoint}/${id}`, player);
  return res.data;
};

export const deletePlayer = async (id) => {
  const res = await httpClient.delete(`${playersEndpoint}/${id}`);
  return res.data;
};

export const getWikiPlayerImage = async (wikidata_id) => {
  console.log('Requesting to Wikidata...');
  const res = await httpClientWiki.get(wikiEndpoint, {
    params: {
      action: 'wbgetclaims',
      format: 'json',
      origin: '*',
      entity: wikidata_id,
      property: 'P18'
    },
  });

  if (res.data.claims && res.data.claims.P18) {
    const file_name = res.data.claims.P18[0].mainsnak.datavalue.value;
    console.log(`URL: https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(file_name)}`);
    return `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(file_name)}`;

  }
  return null;
};

