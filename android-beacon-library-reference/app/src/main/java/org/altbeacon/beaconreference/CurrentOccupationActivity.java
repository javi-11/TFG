package org.altbeacon.beaconreference;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

public class CurrentOccupationActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_current_occupation);
        occupation();
    }

    public void occupation(){
        RequestQueue volleyQueue = Volley.newRequestQueue(CurrentOccupationActivity.this);
        String url = "https://tfg-u3xd.onrender.com/stays/room/occupation";
        TextView oc = (TextView) findViewById(R.id.occupation);
        JSONObject entrada = new JSONObject();
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                ,(Response.Listener<JSONObject>) response-> {

            try {
                String cadena = "";
                String cadenab  = response.getJSONObject("message").toString();
                Map<String, Object> mapping = new ObjectMapper().readValue(cadenab, HashMap.class);
                for(String key : mapping.keySet()){
                    cadena = cadena + key + ": "+ mapping.get(key) + "\n";
                }
                oc.setText(cadena);
            } catch (JSONException e) {
                throw new RuntimeException(e);
            } catch (JsonMappingException e) {
                throw new RuntimeException(e);
            } catch (JsonParseException e) {
                throw new RuntimeException(e);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }

        },
                (Response.ErrorListener) error -> {
                    // make a Toast telling the user
                    // that something went wrong
                    Toast.makeText(CurrentOccupationActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                    // log the error message in the error stream
                    error.printStackTrace();
                    Log.e("MainActivity", error.toString());
                    Log.e("MainActivity", url);


                });
        volleyQueue.add(jsonObjectRequest);
    }
}