package org.altbeacon.beaconreference;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
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

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.ParseException;
import java.text.SimpleDateFormat;

public class StatsActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_stats);
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



    public void onSearchStatsClicked(View view){
        RequestQueue volleyQueue = Volley.newRequestQueue(StatsActivity.this);
        String url = "https://tfg-u3xd.onrender.com/stays/room/most_used";
        String url2 = "https://tfg-u3xd.onrender.com/stays/room/most_used_per_hour";
        JSONObject entrada = new JSONObject();

        EditText input = (EditText) findViewById(R.id.dayFilterText);
        TextView room = (TextView) findViewById(R.id.salaMasOcupada2);
        TextView top = (TextView) findViewById(R.id.horasPuntas2);
        if(isValidDate(input.getText().toString())){
            try{
                entrada.put("day", input.getText().toString());
            } catch(JSONException e){
                e.printStackTrace();
            }


            JsonObjectRequest jsonRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                    ,(Response.Listener<JSONObject>) response-> {

                try {
                    room.setText(response.get("message").toString());
                    room.setVisibility(View.VISIBLE);
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }
            },
                    (Response.ErrorListener) error -> {
                        // make a Toast telling the user
                        // that something went wrong
                        Toast.makeText(StatsActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                        // log the error message in the error stream
                        error.printStackTrace();
                        Log.e("MainActivity", error.toString());
                        Log.e("MainActivity", url);
                        Log.e("MainActivity", entrada.toString());

                    });
            JsonObjectRequest jsonRequest2 = new JsonObjectRequest(Request.Method.POST,url2,entrada
                    ,(Response.Listener<JSONObject>) response-> {

                try {
                    top.setText(response.get("message").toString());
                    top.setVisibility(View.VISIBLE);
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }
            },
                    (Response.ErrorListener) error -> {
                        // make a Toast telling the user
                        // that something went wrong
                        Toast.makeText(StatsActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                        // log the error message in the error stream
                        error.printStackTrace();
                        Log.e("MainActivity", error.toString());
                        Log.e("MainActivity", url);
                        Log.e("MainActivity", entrada.toString());

                    });


            volleyQueue.add(jsonRequest);
            volleyQueue.add(jsonRequest2);
        }
        else{
            Toast.makeText(this, "La fecha no tiene un formato adecuado, por favor introduce una fecha con el formato YYYY-MM-DD", Toast.LENGTH_SHORT).show();
        }
    }
}