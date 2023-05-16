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

public class OccupationActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_occupation);
    }

    public void onFilterClicked(View view){
        RequestQueue volleyQueue = Volley.newRequestQueue(OccupationActivity.this);
        String url = "https://tfg-u3xd.onrender.com/stays/room/hours";
        JSONObject entrada = new JSONObject();
        EditText input = (EditText) findViewById(R.id.startDateText);
        EditText input2 = (EditText) findViewById(R.id.endDateText);
        EditText input3 = (EditText) findViewById(R.id.RoomNameText);
        TextView mensaje = (TextView) findViewById(R.id.Mensaje);

        if(isValidDateTime(input.getText().toString()) && isValidDateTime(input2.getText().toString())){


            try{
                entrada.put("room_name",input3.getText().toString());
                entrada.put("hour1", input.getText().toString());
                entrada.put("hour2",input2.getText().toString());
            } catch(JSONException e){
                e.printStackTrace();
            }


            JsonObjectRequest JsonObjectRequest = new JsonObjectRequest(Request.Method.POST,url,entrada
                    ,(Response.Listener<JSONObject>) response-> {
                try {
                    mensaje.setText("En la sala " + input3.getText().toString() + " ha habido " + response.get("message").toString() + " persona/s entre " + input.getText().toString() + " y " + input2.getText().toString() + ".");
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }

            },
                    (Response.ErrorListener) error -> {
                        // make a Toast telling the user
                        // that something went wrong
                        Toast.makeText(OccupationActivity.this, "Se está reactivando el servidor, vuelve a intentarlo en un minuto", Toast.LENGTH_LONG).show();
                        // log the error message in the error stream
                        error.printStackTrace();
                        Log.e("MainActivity", error.toString());
                        Log.e("MainActivity", url);
                        Log.e("MainActivity", entrada.toString());

                    });
            volleyQueue.add(JsonObjectRequest);
        }
        else{
            Toast.makeText(this, "Una de las dos entradas no tiene un formato adecuado, por favor introduce una fecha con el formato YYYY-MM-DD HH:MM:SS", Toast.LENGTH_SHORT).show();
        }
    }
    public static boolean isValidDateTime(String inDate) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        dateFormat.setLenient(false);
        try {
            dateFormat.parse(inDate.trim());
        } catch (ParseException pe) {
            return false;
        }
        return true;
    }
}