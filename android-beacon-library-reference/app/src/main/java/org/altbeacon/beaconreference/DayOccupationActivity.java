package org.altbeacon.beaconreference;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

public class DayOccupationActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_day_occupation);
    }

    public void Filter(View view) {
        RequestQueue volleyQueue = Volley.newRequestQueue(DayOccupationActivity.this);
        String url = "https://tfg-u3xd.onrender.com/stays/room/occupation_by_hour";
        String url2 = "https://tfg-u3xd.onrender.com/stays/mean";
        JSONObject entrada = new JSONObject();
        EditText input = (EditText) findViewById(R.id.dayFilter);
        TextView oc = (TextView) findViewById(R.id.occupation);
        TextView oc2 = (TextView) findViewById(R.id.mean);
        EditText room_name = (EditText) findViewById(R.id.roomNameText);
        if (isValidDate(input.getText().toString())) {
            try {
                entrada.put("day", input.getText().toString());
                entrada.put("room_name", room_name.getText().toString());
            } catch (JSONException e) {
                e.printStackTrace();
            }

            JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, url, entrada
                    , (Response.Listener<JSONObject>) response -> {
                try {
                    String cadena = "";
                    String cadenab = response.getJSONObject("message").toString();
                    TreeMap<String, Object> mapping = new ObjectMapper().readValue(cadenab, TreeMap.class);

                    for (String key : mapping.keySet()) {
                        String hAux;
                        Integer horaAux = Integer.valueOf(key.substring(0, 2)) + 1;
                        if (horaAux < 10)
                            hAux = "0" + horaAux.toString();
                        else {
                            hAux = horaAux.toString();
                        }
                        cadena = cadena + "Franja horaria: " + key + " - " + hAux + ":00" + " -> " + mapping.get(key) + " personas." + "\n";
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
                        Toast.makeText(DayOccupationActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                        // log the error message in the error stream
                        Log.e("MainActivity", "loadDogImage error: ${error.localizedMessage}");
                    });
            JsonObjectRequest jsonObjectRequest2 = new JsonObjectRequest(Request.Method.POST, url2, entrada
                    , (Response.Listener<JSONObject>) response -> {

                String cadena = null;
                try {
                    cadena = response.get("message").toString();
                    oc2.setText("La media de ocupación de " + room_name.getText().toString() + " durante el día " +input.getText().toString()+ " fue de " + cadena +" personas.");
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }

            },
                    (Response.ErrorListener) error -> {
                        // make a Toast telling the user
                        // that something went wrong
                        Toast.makeText(DayOccupationActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                        // log the error message in the error stream
                        Log.e("MainActivity", "loadDogImage error: ${error.localizedMessage}");
                    });



            volleyQueue.add(jsonObjectRequest);
            volleyQueue.add(jsonObjectRequest2);
        } else {
            Toast.makeText(this, "La fecha no tiene un formato adecuado, por favor introduce" +
                    " una fecha con el formato YYYY-MM-DD", Toast.LENGTH_SHORT).show();

        }

    }

    public static boolean isValidDate(String inDate) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        dateFormat.setLenient(false);
        try {
            dateFormat.parse(inDate.trim());
        } catch (ParseException pe) {
            return false;
        }
        return true;
    }
}